Unwrapping Cylindrical Meshes to Structured Grids
-------------------------------------------------

to handle meshes we have the following libraries, pyvista and CGALMethods. At the moment bot libraries are not interoperable
however they can both read directly from vtk files.

.. code-block:: python

   import pymethods as pma
   import pyvista as pv
   import pathlib as pt
   import time

   openfoam_vtk_folder = pt.Path("../../Datasets/openfoam_vtk")
   surface_vtk_path = openfoam_vtk_folder/"WALL/WALL_400.vtk"
   # vtk mesh read via pyvista
   vtk_mesh = pv.read(surface_vtk)
   # vtk mesh read via CGAL Methods
   cgal_mesh = pma.CGALMethods.SurfaceMesh(surface_vtk.as_posix())

two methods have been explored for the parameterization of a 3D unstructed cylindrical mesh to 3D structured grids.
In the first method the cylindrical mesh is parameterized by a border constructed from the inlet and outlet vertices
combined with a seam connnecting the two. The method is performed via the CGALMethods library.

.. code-block:: python

   # with the following method we unwrap the artery using CGAL and then map the solution to a grid
   unwrapped_cgalmesh = pma.CGALMethods.SurfaceMesh(cgal_mesh)
   gridded = CM.map_parameterized_mesh_to_grid(unwrapped)

points can be supplied to specify the location of the inlet such thatthe unwrapping is correctly oriented

.. code-block:: python

   # with the following method we unwrap the artery using CGAL and then map the solution to a grid
   unwrapped_cgalmesh = pma.CGALMethods.SurfaceMesh(cgal_mesh, *point) # where the point e.g. [1,2,,3]
   gridded = CM.map_parameterized_mesh_to_grid(unwrapped)


in the second method if the centerline is known the mesh is unwrapped via slicing the mesh along the centerline using planes
whose normals are specified by the tangents of the centerline. This has been performed using pyvista.

.. code-block::python

   # the centerline finder method requires a cgal mesh
   centerline = pma.algorithms.unwrapping.get_centerline_from_cylindrical_mesh(cgal_mesh)

   # the centerline returned is an object parameterized by its arclength so we can obtain equally spaced points through the following
   centerline = centerline(np.linspace(0,1, 384))

   # now we can unwrap the vtk mesh using the cgal mesh, as of yet cgal and vtk have not been properly integrated
   vtk_mesh = pma.algorithms.unwrapping.unwrap_cylinder_vtk_from_centerline(centerline, vtk_mesh, points_per_contour=256)


NOTE: the centerline finding algorithm currently employed requires a cgal mesh.

.. code-block::python

   # the centerline finder method requires a cgal mesh
   centerline = pma.algorithms.unwrapping.get_centerline_from_cylindrical_mesh(cgal_mesh)
