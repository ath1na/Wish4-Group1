"""
Implementation of what is presented in slide 62. Given a list of submeshes, we craft latent codes and compare them to figure out which parts can be used as primitives.
# TODO: 
- code this with pytorch
- Try to input latent codes obtained from a NN
 """


"""from stl import mesh"""
import torch 
import os
import trimesh
import numpy as np


def load_mesh(filepath):
    mesh = trimesh.load(filepath)
    return mesh


def load_parts(dir='sample_chair'):
    """Load each mesh part from the test chair directory"""
    meshes = []
    for i in range(1, 11):
        print(os.path.join('..', dir, f'p{i}.stl'))
        mesh = load_mesh(os.path.join(dir, f'p{i}.stl'))
        meshes.append(mesh)
    return meshes


def compute_pca(X):
    '''
    Compute pca components
    :param X (Nx3): array containing one data per line
    :return: mxn numpy array where m*n = X.shape[1]
        B (Nx3) is the principal vectors
        L (3) is the variance 
        M (3) is the mean
    '''
    import numpy as np
    nSamples = X.shape[0]
    M = np.mean(X, 0)

    # Centered data matrix normalized
    X = (X - np.tile(M, (nSamples, 1)))
    U, S, V = np.linalg.svd(X, full_matrices=False)
    Sd = np.diag(S)
    # print np.allclose(X, np.dot(U, np.dot(Sd, V)))
    B = V.T
    Z = U.dot(Sd)

    # When using the data matrix instead of the covariance the diagonal of S is the square root of the eigenvalues
    L = (S ** 2) / (nSamples - 1)  # Variance
    Sigma = L ** 0.5  # Std

    return B, M, L



def encode_mesh(mesh):
    """Given a mesh, return a 1D latent vector of fixed length K"""
    v = np.array(mesh.vertices)
    B, M, Var = compute_pca(v)
    latent = np.concatenate([abs(B.reshape(-1)), Var]) # We take abs because the eigen vectors orientation is arbitrary
    assert len(latent.shape) == 1, 'Latent vector should be one dimension'
    return latent


def compute_latent_matrix(data_folder='sample_chair'):
    """Given a folder containing P parts, create a PxK matrix, where each line represents the latent code for one part."""
    meshes = load_parts()

    latent_codes = []
    for mesh in meshes:
        latent = encode_mesh(mesh)
        latent_codes.append(latent)

    M = np.vstack(latent_codes)

    return M

def print_parts_correspondances(D_th):
    for i in range(D_th.shape[0]):
        ids = np.where(D_th[i,:])
        print(f'Part {i}: {ids}')

def get_primitives(D_th):
    prim_indices = [0]
    # from ipdb import set_trace; set_trace()
    for i in range(1, D_th.shape[0]):
        print(i, np.concatenate( np.where(D_th[:i,:])))
        if i not in np.concatenate( np.where(D_th[:i,:])):
            prim_indices.append(i)
    return prim_indices



if __name__ == "__main__":
    
    torch.set_printoptions(sci_mode=False)
    torch.set_printoptions(precision=2)
    
    # Create an array of size PxK where each line represents the latent code for one part
    m_lat = compute_latent_matrix(data_folder='sample_chair')
    m_lat = torch.tensor(m_lat)
    print(m_lat)

    # Generate the matrix of the part2part distance (in the sence of difference)
    D = torch.cdist(m_lat, m_lat, p=2.0)
    assert D.shape == (m_lat.shape[0], m_lat.shape[0])

    print(D)

    # Compute the matrix of correspondances
    th = 1 # This is defined arbitrary given the values of D
    D_th = D<1
    print(D_th)
    print_parts_correspondances(D_th)

    # Get the primitives out of the matrix
    print(f'Matrix Dth rank : {np.linalg.matrix_rank(D_th.numpy())}') # todo in torch
    prim_indices = get_primitives(D_th)
    print(f'Primitives indices: {prim_indices}')
    str_prim = [f'P{i+1}' for i in prim_indices]
    print(f'The object primitives are {str_prim}')
