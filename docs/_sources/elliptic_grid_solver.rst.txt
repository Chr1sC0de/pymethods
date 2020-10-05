Elliptic Grid Solvers
---------------------

After performing a transfinite interpolation on a 2D contour we may wish to refine the generated solution.
We can do so via an elliptic grid solver.

.. code-block:: Python

   # settting things up

   import numpy as np
   import pymethods as pma
   from pymethods.algorithms.transfinite_interpolation import Transfinite2d
   from pymethods import pyplot as plt
   import scipy
   from pymethods.algorithms import elliptic_mesh_generation
   import pathlib as pt

   cwd = pt.Path(__file__).parent

   dataset_folder = cwd/'../../Datasets/artery_structure_grid'
   data_file = dataset_folder/'00000.npz'
   data = np.load(data_file)
   oct_pts = data["points"]

   inner = np.s_[1:-1]
   ip1 = np.s_[2:]
   im1 = np.s_[0:-2]

   # apply a for loop for the desired contours within the contour stack
   for contour_id in [10, ]:
      ...

Let us load a contour and transfinitely interpolate with `Transfinite2d`

.. code-block:: Python

   oct_contour = pma.arrays.Contour(
            oct_pts[:, :, contour_id]
         )

   # as the method is 2-dimensional we will retain the basis and
   # the centroid of the contour to flatten the grid
   centroid = oct_contour.centroid
   basis = oct_contour.calc_basis()

   transfinite_interpolator = Transfinite2d(
      oct_contour
   )

   # the total number of points along each segment used for interpolation
   N = 30

   grid, (zeta_orig, eta_orig) = transfinite_interpolator.pts_mesh_uniform(
      N, N, return_params=True)

