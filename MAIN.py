import bpy
import os
import numpy as np
import random 
import bmesh
import math

import imp
from PIL import Image
from mathutils import Euler, geometry
import builtins 


from mathutils import Vector, Matrix
from math import degrees






            

def add_background():
    bpy.ops.mesh.primitive_plane_add(radius=2, view_align=False, location=(0.5, -0.5, 0), rotation=(0, 0, 0))
    activeObject = bpy.context.active_object #Set active object to variable
    activeObject.data.name = "Background" 
    if 'Red' not in bpy.data.materials:
        mat = bpy.data.materials.new(name="Red") #set new material to variable
        mat.diffuse_color = (0,0,0)
        mat.specular_intensity = 0
        mat.use_shadeless = True
    mat = bpy.data.materials.get('Red')
    activeObject.data.materials.append(mat) #add the material to the object
    bpy.context.object.active_material.diffuse_color = (0, 0, 0) #change color
    bpy.context.object.active_material.specular_intensity = 0
    bpy.context.object.active_material.use_shadeless = True

def add_object(directory, filename):
    path = directory + filename
    bpy.ops.import_scene.obj(filepath=path)


def write_obj(filepath):
    out = open(filepath, 'w')
    ob = bpy.context.active_object
    mesh = ob.data
    for vert in mesh.vertices:
        out.write('v %f %f %f\n' % (vert.co.x, vert.co.y, vert.co.z))

    for face in mesh.polygons:
        out.write('f')

    for vert in face.vertices:
        out.write(' %i' % (vert + 1))
        out.write('\n')

    out.close()


# import all obj files from the given directory, update matrices with the file names, and initialize the translations rotations and scalings since these can change later in the pipeline
def import_parts(directory, names, objects, translations, rotations, scalings):
    #mesh = bpy.data.meshes.new('Mesh')
    #total = bpy.data.objects.new('TOTAL', mesh)

    #objects.append(total)
    objects_to_merge = []
    for file in os.listdir(directory):
        if file.endswith(".obj"):
            print(file)
            add_object(directory, file)
            
            file = file.split(".")[0]
            names.append(file)
            objects.append(bpy.data.objects[file])
            translations.append(Matrix.Translation((0, 0, 0)))
            rotations.append(Matrix.Rotation(math.radians(0), 4, 'X'))
            scalings.append(Matrix.Scale(1, 4, (0,0,0)))
            color_face = bpy.data.materials.new(file)
            # color_face.shadow_method = 'NONE' #change for python 2.82
            color_face.use_shadeless = True
            
            #bpy.data.objects[file].rotation_euler.x = 0
            #bpy.data.objects[file].matrix_world = bpy.data.objects[file].matrix_world * Matrix.Rotation(math.radians(-90), 4, 'X')
            #bpy.ops.transform.rotate(value=(math.radians(180)),axis=(1.0,0.0,0.0))
            bpy.ops.object.transform_apply( rotation = True )
            id = float(file.split("-")[1])
            color_face.diffuse_color = [0.9, 0.9, 0.9]
            bpy.data.objects[file].data.materials.append(color_face)
            copy_obj = bpy.data.objects.new("total", bpy.data.objects[file].data.copy())
            bpy.context.scene.objects.link(copy_obj)
            objects_to_merge.append(copy_obj)
            
    context = bpy.context.copy()
    context['active_object'] = objects_to_merge[0]
    context['selected_objects'] = objects_to_merge
    context['selected_editable_bases'] = [bpy.context.scene.object_bases[ob.name] for ob in objects_to_merge]
    bpy.ops.object.join(context)

    names.insert(0, "total") 
    total_obj = bpy.data.objects['total']
    objects.insert(0, total_obj)
    bpy.context.scene.objects.active = total_obj
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.002)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()
    
    for object in objects:
        bpy.context.scene.objects.active = object
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete_loose()
        bpy.ops.object.editmode_toggle()
    
    

def normalize_parts(objects):
    ratio, v3ctor = normalize_obj(objects)
    objects[0].select = True
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    move = - objects[0].location 
    objects[0].select = False
    
    #for i_obj in range(0, len(objects)):
         #obj = objects[i_obj]
         #scale_matrix = Matrix.Identity(4)
         #scale_matrix = ratio * scale_matrix
         #for v in objects[i_obj].data.vertices:
         #    v.co = scale_matrix * v.co
         #for vert in  objects[i_obj].data.vertices:
         #   vert.co.x = ratio * (vert.co.x)
         #   vert.co.y = ratio * (vert.co.y)
         #   vert.co.z = ratio * (vert.co.z)
    for i_obj in range(0, len(objects)):
         objects[i_obj].select = True
         objects[i_obj].location = objects[i_obj].location + move
         bpy.context.scene.objects.active = objects[i_obj]
         bpy.ops.object.transform_apply(location = True, rotation = True, scale = False)
         objects[i_obj].select = False
         bpy.ops.object.editmode_toggle()
         bpy.ops.mesh.select_all(action='SELECT')
         bpy.ops.mesh.normals_make_consistent(inside=False)
         bpy.ops.object.editmode_toggle()
         bpy.context.scene.objects.active = None
         
    return ratio, v3ctor, move

# normalize the object to fit into the unit cube
def normalize_obj(objects):
    #ob = bpy.context.active_object
    ob = objects[0]
    mesh = ob.data
    min_x = mesh.vertices[0].co.x
    max_x = mesh.vertices[0].co.x
    min_y = mesh.vertices[0].co.y
    max_y = mesh.vertices[0].co.y
    min_z = mesh.vertices[0].co.z
    max_z = mesh.vertices[0].co.z
    for vert in mesh.vertices:
        if vert.co.x < min_x:
            min_x = vert.co.x
        if vert.co.y < min_y:
            min_y = vert.co.y
        if vert.co.z < min_z:
            min_z = vert.co.z
            
            
        if vert.co.x > max_x:
            max_x = vert.co.x
        if vert.co.y > max_y:
            max_y = vert.co.y
        if vert.co.z > max_z:
            max_z = vert.co.z


    x_dim = max_x - min_x
    y_dim = max_y - min_y
    z_dim = max_z - min_z

    ratio = 1.0 / x_dim

    if y_dim > x_dim and y_dim > z_dim:
        ratio = 1.0 / y_dim

    if z_dim > x_dim and z_dim > y_dim:
        ratio = 1.0 / z_dim
   
    for i_obj in range(0, len(objects)):

         for vert in  objects[i_obj].data.vertices:
            vert.co.x = ratio * (vert.co.x - min_x)
            vert.co.y = ratio * (vert.co.y - min_y)
            vert.co.z = ratio * (vert.co.z - min_z)    

    
    return(ratio, Vector((min_x, min_y, min_z)))




# Compute logic difference between different obj files
def find_difference(names, connections, volumes):
    print(" Calling find connections for intersections..")
    for idx_o in range(len(names)):
        obj_ = bpy.data.objects[names[idx_o]]
        bpy.context.scene.objects.active = obj_
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.fill_holes(sides = 100)
        bpy.ops.object.editmode_toggle()
    for idx_o_1 in range(len(names)):
        for idx_o_2  in range(len(names)):
            if(idx_o_1 != 0 and idx_o_1 < idx_o_2):
                obj_1 = bpy.data.objects[names[idx_o_1]]
                obj_2 = bpy.data.objects[names[idx_o_2]]
                me_1 = obj_1.data
                bm_1 = bmesh.new()
                bm_1.from_mesh(me_1)
                bmesh.ops.recalc_face_normals(bm_1, faces=bm_1.faces)
                bm_1.faces.ensure_lookup_table()
                vol_1 = bm_1.calc_volume()

                me_2 = obj_2.data
                bm_2 = bmesh.new()
                bm_2.from_mesh(me_2)
                bmesh.ops.recalc_face_normals(bm_2, faces=bm_2.faces)
                bm_2.faces.ensure_lookup_table()
                vol_2 = bm_2.calc_volume()

                mesh_intersection = bpy.data.meshes.new('difference_'+names[idx_o_1]+" "+names[idx_o_2])
                if (vol_1 > vol_2):
                    bm_1.to_mesh(mesh_intersection)
                else:
                    bm_2.to_mesh(mesh_intersection)
                obj_intersection = bpy.data.objects.new( 'difference_'+names[idx_o_1]+" "+names[idx_o_2], mesh_intersection )
                bpy.context.scene.objects.link( obj_intersection )
                bpy.context.scene.objects.active = obj_intersection
                obj_intersection.select = True
                bpy.ops.object.modifier_add(type = 'BOOLEAN')
                bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
                if (vol_1 > vol_2):
                    bpy.context.object.modifiers["Boolean"].object = obj_2
                else:
                    bpy.context.object.modifiers["Boolean"].object = obj_1
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")


                #bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                mesh_ = obj_intersection.data
                connection = False
                vert_mean = Vector((0,0,0))
                
                for vertex in mesh_.vertices:
                    vert_mean += vertex.co
                 
                #d   = mesh_.to_mesh() # Create a temporary mesh with modifiers applied
                #bm  = bmesh.from_edit_mesh( mesh_ )
                bm = bmesh.new()
                bm.from_mesh(mesh_)
                vol = bm.calc_volume()
                volumes.append(vol)

                print(names[idx_o_1], ", ", names[idx_o_2], ": ")
                if( len(mesh_.vertices) > 10 ):
                    #connection = True
                    #vert_mean /= len(mesh_.vertices)
                    #connections[idx_o_1, idx_o_2] = vert_mean + obj_intersection.location
                    print( "Intersection volume for ",names[idx_o_1], " with volume ",vol_1, " and ", names[idx_o_2], " with volume ",vol_2, " is: ", vol)
                    #bpy.ops.mesh.primitive_ico_sphere_add(location=connections[idx_o_1, idx_o_2], size=0.02)
                    #bpy.context.active_object.name = "difference_"+names[idx_o_1]+" "+names[idx_o_2]
                #if( len(mesh_.vertices) <= 10 ):
                # Deselect all
                bpy.ops.object.select_all(action='DESELECT')
    
                # Select the object
                #obj_intersection.select = True    # Blender 2.7x
    
                #bpy.ops.object.delete() 
