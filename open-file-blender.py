
import MAIN
import imp
import bpy
import numpy as np
imp.reload(MAIN)


names = []

translations = []

rotations = []

scalings = []

objects = []

frames = []

volumes = []

directory = "models\\z_legs\\objs\\"

outname = "out_test.obj"

# bpy.ops.wm.open_mainfile(filepath="output.blend")

MAIN.import_parts(directory, names, objects, translations, rotations, scalings)

ratio, v3ctor, move = MAIN.normalize_parts(objects) # Assumption that at the origin is placed the union of all the pieces structured as the object.

differences = np.empty( shape=(len(frames) , len(frames) ), dtype=np.object)

MAIN.find_difference(names, differences, volumes)

print("Finished computations..")


#write_obj(directory + outname)

bpy.ops.wm.save_as_mainfile(filepath="output.blend")




