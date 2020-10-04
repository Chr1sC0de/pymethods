import numpy as np
import pymethods as pma
from pymethods.algorithms.transfinite_interpolation import Transfinite2d
import pathlib as pt


if __name__ == "__main__":

    cwd            = pt.Path(__file__).parent
    dataset_folder = cwd/'../../Datasets/artery_structure_grid'
    data_file      = dataset_folder/'00000.npz'
    data           = np.load(data_file)
    oct_pts        = data["points"]

    dims, c_n, l_n = oct_pts.shape

    uniform_grid   = []

    row, cols = 5, 5

    for i in range(10, l_n, 30):

        contour     = pma.arrays.FlatContour(oct_pts[:, :, i]).filter(11, 3)
        transfinite = pma.algorithms.transfinite_interpolation.Transfinite2d(contour)
        tmp_grid    = transfinite.pts_mesh_uniform(row, cols)

        uniform_grid.append(tmp_grid)

        ax = contour.plot3d(color="blue", alpha=0.5)
        pma.pyplot.plot_grid3d(
            tmp_grid, ax=ax, alpha=0.2, color="green")
        pma.pyplot.scatter3d(
            *tmp_grid.reshape(3, -1), s=10, ax=ax, alpha=1, color="blue")

    uniform_grid = np.stack(uniform_grid, axis=-1)

    for i in range(row):
        for j in range(cols):
            pma.pyplot.plot3d(
                *uniform_grid[:, i, j,:],
                linewidth=0.25, color="blue", linestyle="--", ax=ax, alpha=1)

    pma.pyplot.axis("off")

    pma.pyplot.equal_aspect_3d()
    pma.pyplot.show()
