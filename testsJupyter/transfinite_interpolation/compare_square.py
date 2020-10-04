import numpy as np
import pymethods as pma
from pymethods.algorithms.transfinite_interpolation import Transfinite2d
import pathlib as pt

label_fontsize = 20

if __name__ == "__main__":

    cwd            = pt.Path(__file__).parent
    dataset_folder = cwd/'../../Datasets/artery_structure_grid'
    data_file      = dataset_folder/'00000.npz'
    data           = np.load(data_file)
    oct_pts        = data["points"]
    contour_id     = 50

    oct_contour = pma.arrays.FlatContour(oct_pts[:,:, contour_id]).filter(11, 3)

    (r1, r2, r3, r4) = oct_contour.transfinite_quarter(npts=200)

    transfinite = pma.algorithms.transfinite_interpolation.TransfiniteDomain(
        r1, r2, r3, r4)

    square_1             = pma.arrays.contourShapes.Square(1, npts=100)
    (s1, s2, s3, s4)     = square_1.transfinite_quarter(npts=100)
    square_2             = pma.arrays.contourShapes.Square(
                                0.5, npts=100, corner=[0.25, 0.25, 0])
    (sa1, sa2, sa3, sa4) = square_2.transfinite_quarter(npts=100)
    transfinite_square   = \
        pma.algorithms.transfinite_interpolation.TransfiniteDomain(
            s1, s2, s3, s4)

    ra1 = transfinite(*sa1[:2])
    ra2 = transfinite(*sa2[:2])
    ra3 = transfinite(*sa3[:2])
    ra4 = transfinite(*sa4[:2])

    #---------------------------------------------------------------------------
    # transfinite along the grid points
    npts           = 10
    points_contour = transfinite.pts_mesh_column_uniform(npts, npts)
    points_square  = transfinite_square.pts_mesh_column_uniform(npts, npts)

    uniform_contour = transfinite.pts_mesh_uniform(npts, npts)
    uniform_square  = transfinite_square.pts_mesh_uniform(npts, npts)
    #---------------------------------------------------------------------------

    f    = pma.pyplot.figure()
    ax_1 = f.add_subplot(1, 2, 1)

    shared_kwargs = {"loc":0.4, "ax": ax_1}

    pma.pyplot.plot_stream2d(s1, s3, color="green", **shared_kwargs)
    pma.pyplot.plot_stream2d(s2, s4, color="red"  , **shared_kwargs)

    pma.pyplot.plot_stream2d(sa1, sa3, color="green", **shared_kwargs)
    pma.pyplot.plot_stream2d(sa2, sa4, color="red"  , **shared_kwargs)

    pma.pyplot.plot_grid2d(uniform_square, "b", ax=ax_1, alpha=0.3)

    ax_1.scatter(*points_square[:2], color="blue", s=10)

    ax_1.set_aspect("equal")
    alpha = 0.125
    ax_1.set_xlim([-alpha, 1 + alpha])
    ax_1.set_ylim([-alpha, 1 + alpha])

    shared_kwargs = {"fontsize": label_fontsize, "labelpad": 15}

    ax_1.set_xlabel(r"$\xi$",  **shared_kwargs)
    ax_1.set_ylabel(r"$\eta$", **shared_kwargs)

    ax_1.tick_params(axis='both', which='major', labelsize=15)
    ax_1.minorticks_on()

    #---------------------------------------------------------------------------

    ax_2 = f.add_subplot(1, 2, 2, projection="3d")
    shared_kwargs = {"loc":0.5, "arrow_length_ratio":1.5, "ax": ax_2}

    pma.pyplot.plot_stream3d(r1, r3, color="green", **shared_kwargs)
    pma.pyplot.plot_stream3d(r2, r4, color="red"  , **shared_kwargs)

    pma.pyplot.plot_stream3d(ra1, ra3, color="green", **shared_kwargs)
    pma.pyplot.plot_stream3d(ra2, ra4, color="red"  , **shared_kwargs)

    shared_kwargs = {"labelpad": 25, "fontsize": label_fontsize}

    ax_2.set_xlabel(r"x", **shared_kwargs)
    ax_2.set_ylabel(r"y", **shared_kwargs)
    ax_2.set_zlabel(r"z", **shared_kwargs)

    ax_2.tick_params(axis='both', which='major', labelsize=15, pad=10)

    ax_2.scatter(*points_contour, color="blue", s=10)

    pma.pyplot.plot_grid3d(uniform_contour, color="blue",ax=ax_2, alpha=0.3)
    pma.pyplot.equal_aspect_3d(ax_2)
    pma.pyplot.show()