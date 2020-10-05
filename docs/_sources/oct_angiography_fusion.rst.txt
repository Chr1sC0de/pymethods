OCT+Angiography Fusion
----------------------

Angiography data extracted via QAngio XA 3D RE and OCT data that has been extracted via QIvus
can be read, combined and meshed quickly through the construct module,


.. code-block:: python

   import pymethods as pma
   import pathlib as pt

   path = pt.Path(r'../../Datasets/test_1')
   construct_vessel = pma.construct.ivoct.VesselSurface(path)

   surface = construct_vessel.construct(
      mm_per_frame=mm_per_frame,
      mm_per_pixel=mm_per_pixel,
      processors=4,
      surface_filter=25,
      interpolate_contours=360,
      centerlineResolution=0.001,
   )
   p = pv.BackgroundPlotter()
   mesh = surface.to_vtk()
   p.add_mesh(mesh)
   p.show()

where mm_per_frame and mm_per_pixel are provided by the user.

processors defines how may processsors to be used during image parsing

the surface_filters is the window size used to smooth the surface

interpolate_contours are total points per contour

centerlineResolutions is the smallest distance between cross sectional contours along the surface

