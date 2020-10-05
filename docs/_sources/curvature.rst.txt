Curvature Calculation
---------------------


.. code-block::python

   import pymethods as pma
   import pyvista as pv
   import pathlib as pt
   import time
   openfoam_vtk_folder = pt.Path("../../Datasets/openfoam_vtk")
   surface_vtk = openfoam_vtk_folder/"WALL/WALL_400.vtk"
   # have not yet had the time to integrate pyvista with cgal
   vtk_mesh = pv.read(surface_vtk)
   cgal_mesh = pma.CGALMethods.SurfaceMesh(surface_vtk.as_posix())


We present the following methods. In the first method a CGAL surface mesh is required. This method fits a polynomial to the surface


.. code-block:: python

   start = time.time()
   k_max_monge, k_min_monge = pma.algorithms.curvature_fitting.monge_surface_mesh_fitting(
      cgal_mesh, d_fitting=3, d_monge=3, knn=300, internal=True
   )
   end = time.time()

   print("time taken:", end-start)


If only points are available the following method applies normal section fitting


.. code-block:: python

   # if the data is a set of points, we can apply the normal section fitting method
   points = surface_mesh.points()

   start = time.time()
   # assumes the points are in the form dims * points
   point_surface = pma.arrays.Pointsurface(points.T)
   # the following is the is ordered max, min and ordered principal directions
   k_max_min, d_max_min = point_surface.compute_principle_curvatures(
      neighbours=300, external=False
   )
   end = time.time()

   print(end-start)


we can plot the results of the first and second methods


.. code-block:: python

   plotter_1 = pv.BackgroundPlotter()
   mesh_1 = pv.PolyData(points)
   mesh_1.point_arrays['max_curvature'] = k_max_monge
   plotter_1.add_mesh(mesh_1)
   plotter_1.show()

   plotter_2 = pv.BackgroundPlotter()
   mesh_2 = pv.PolyData(points)
   mesh_2.point_arrays['max_curvature'] = k_max_min[0]
   plotter_2.add_mesh(mesh_2)
   plotter_2.show()