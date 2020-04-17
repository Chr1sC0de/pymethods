Pointwise Glyphs for Autmatic Mesh Generation
---------------------------------------------

To allow for easier automation and consistent CFD mesh generation the `templates.make_glf_stl_to_foammake_glf_stl_to_foam`,

.. code-block:: Python

   import pymethods as pma

   pma.templates.make_glf_stl_to_foam(
      './shape.stl',
      delta_s                       = 0.1,
      TRexGrowthRate1               = 1.3,
      TRexGrowthRate                = 1.1,
      TRexMaximumLayers             = 6,
      TRexSkewCriteriaMaximumAngle1 = 180,
      TRexSkewCriteriaMaximumAngle  = 170,
      setSpacing                    = 0.025,
      polymesh_folder               = '.',
      pointwise_name                = 'foam_project.pw',
      file_name                     = 'stl_to_foam.glf'
   )

The above code will generate a pointwise glyph which automates the construction of an OpenFoam mesh. Running the glyph will automatically call pointwise,
creating the pointwise polymesh in the folder specified by the user