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

all_ids = np.arange(0, 100, 10)

connected_groups = []

for contour_id in all_ids:
    oct_contour = pma.arrays.FlatContour(
        oct_pts[:,:, contour_id]
    ).filter(11, 3)

    transfinite_interpolator = Transfinite2d(oct_contour)
    square = pma.arrays.contourShapes.Square(
        0.5, npts=100, corner=[0.25, 0.25, 0])[0:2]

    npts = 100

    middle = transfinite_interpolator(*square)

    connector1 = transfinite_interpolator(
        np.linspace(0, 0.25, npts), np.linspace(0, 0.25, npts))
    connector2 = transfinite_interpolator(
        np.linspace(0, 0.25, npts), np.linspace(1, 0.75, npts))
    connector3 = transfinite_interpolator(
        np.linspace(1, 0.75, npts), np.linspace(0, 0.25, npts))
    connector4 = transfinite_interpolator(
        np.linspace(1, 0.75, npts), np.linspace(1, 0.75, npts))

    connected_groups.append(
        np.stack(
            (
                connector1[:, 0],
                connector1[:, -1],
                connector2[:, 0],
                connector2[:, -1],
                connector3[:, 0],
                connector3[:, -1],
                connector4[:, 0],
                connector4[:, -1]
            ), axis=0
        )
    )

    oct_contour.plot3d("b", alpha=0.7)
    middle.plot3d("b", alpha=0.7)
    connector1.plot3d("b", alpha=0.5)
    connector2.plot3d("b", alpha=0.5)
    connector3.plot3d("b", alpha=0.5)
    connector4.plot3d("b", alpha=0.5)

connected_groups = np.stack(connected_groups, axis=-1)

for group in connected_groups:
    curve = pma.arrays.Curve(group)
    curve.plot3d("g", alpha=0.5)

pma.pyplot.equal_aspect_3d()
pma.pyplot.show()