Angiography Reconstruction
--------------------------

Angiography data extracted via QAngio XA 3D RE can be read and meshed quickly through the construct module,


.. code-block:: python

   import pymethods as pma
   import pathlib as pt

   path_angio = pt.Path(r'../../Datasets/test_1/angiography')

   mainVesselConstructor = pma.construct.angiography.vessel.Main(
      path_angio
   )
   mainVessel = mainVesselConstructor.construct(window_size=25)
   mainVessel.to_vtk().plot()

   bifVesselConstructor = pma.construct.angiography.vessel.Bifur(
    path_angio
   )
   bifVessel = bifVesselConstructor.construct(window_size=25)
   bifVessel.to_vtk().plot()

where the window size is the size of the filter used to smooth the surfaces


