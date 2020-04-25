Transfinte Interpolation
------------------------

We can perform transfinite interpolation to interpolate a structured grid onto a closed contour. Let us first load the desired data
and modules as well as specify the ids of contours we wish to interpolate transfinitely.

.. code-block:: python

   import numpy as np
   import pymethods as pma
   from pymethods.algorithms.transfinite_interpolation import Transfinite2d
   import pathlib as pt

   cwd = pt.Path(__file__).parent

   dataset_folder = cwd/'../../Datasets/artery_structure '
   data_file = dataset_folder/'00000.npz'
   data = np.load(data_file)
   oct_pts = data["points"]
   contour_id = 0

   all_ids = [0, 50, 100, 150, 200]

now for each contour specified let us transfinitely interpolate the region bounded. We do so by using our `Transfinite2d` class.

.. code-block:: python

   for contour_id in all_ids:
      oct_contour = pma.arrays.Contour(
         oct_pts[:,:, contour_id]
      )

      transfinite_interpolator = Transfinite2d(
         oct_contour
      )


during the transfinite interpolation process the contour is divided into 4 apprixiamtely equally length segments.
The segments are paired. For each pair U, V let us divide the segments into a fixed number of points and plot the results,


.. code-block:: python

   # within the for loop
   n_U = 15
   n_V = 15

   grid = transfinite_interpolator.pts_mesh_uniform(n_U, n_V)

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
