import pymethods as pma

import numpy as np
import pymethods as pma
from pymethods.algorithms.transfinite_interpolation import TransfiniteCylinder
import pathlib as pt

import pyvista as pv

cwd = pt.Path(__file__).parent

dataset_folder = cwd/'../../Datasets/artery_structure_grid'
data_file = dataset_folder/'00000.npz'
data = np.load(data_file)
oct_pts = data["points"]
wss_data = data["wss"]

cylindrical_surface = pma.arrays.structured.CylindricalSurface(oct_pts)

transfinite_interpolator = TransfiniteCylinder(cylindrical_surface)

u = np.linspace(0, 1, 25)
v= np.linspace(0, 1,25)
w = np.linspace(0,1,100)

volume = transfinite_interpolator.pts_mesh(
    u, v, w
)

volume_slice = pma.arrays.Vectorspace(volume[:,:,:,0].reshape(3,-1))

volume_slice.scatter3d()
# pma.pyplot.show()
# print(volume.shape)
vectors = transfinite_interpolator.pts_mesh_column(
    u, v, w
)

vectors.scatter3d()

# original domain
k_mesh.point_arrays['wss'] = wss_data.flatten()
# in the computational domain

# vtk_computational =

print('done')