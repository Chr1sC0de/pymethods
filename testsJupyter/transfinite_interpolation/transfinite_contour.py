import numpy as np
import pymethods as pma
from pymethods.algorithms.transfinite_interpolation import Transfinite2d
import pathlib as pt

cwd = pt.Path(__file__).parent

dataset_folder = cwd/'../../Datasets/artery_structure_grid'
data_file = dataset_folder/'00000.npz'
data = np.load(data_file)
oct_pts = data["points"]
contour_id = 0

all_ids = [0, 50, 100, 150, 200]

for contour_id in all_ids:
    oct_contour = pma.arrays.Contour(
        oct_pts[:,:, contour_id]
    )

    transfinite_interpolator = Transfinite2d(
        oct_contour
    )

    U = np.linspace(0,1,15)
    V = np.linspace(0,1,15)

    grid = transfinite_interpolator.pts_mesh_uniform(15,15)

    x_pts = pma.arrays.Curve(grid[:,0,:])
    y_pts = pma.arrays.Curve(grid[:,:,0])

    x_pts.plot3d('r-')
    y_pts.plot3d('b-')

    x_pts = pma.arrays.Curve(grid[:,-1,:])
    y_pts = pma.arrays.Curve(grid[:,:,-1])

    x_pts.plot3d('r-')
    y_pts.plot3d('b-')

    # plot the horizontal lines
    for i in range(grid.shape[1]):
        pma.arrays.Curve(grid[:,i,:]).plot3d(color='green')
    for i in range(grid.shape[-1]):
        pma.arrays.Curve(grid[:,:,i]).plot3d(color='green')
    interpolated = transfinite_interpolator.pts_mesh_column_uniform(15,15)

    interpolated.scatter3d(color='orange', alpha=0.5)

pma.pyplot.equal_aspect_3d()
pma.pyplot.axis('off')
pma.pyplot.show()