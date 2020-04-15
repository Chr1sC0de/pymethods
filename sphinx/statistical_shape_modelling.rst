Creating a Statistical Shape Model
----------------------------------

we can generate a statistical shape model from the `algorithms.shapeModelling.CylindricalPointModel` method

.. code-block:: Python

   import sys
   import pymethods as pm
   import pyvista as pv

   model = pm.algorithms.shapeModelling.CylindricalPointModel(
   r'../../Datasets\shape_modelling_LADs', structured_shape=(3, 360, 720))
   model.build(scale=True)

we start by specifying the folder where the shape vtks are stored and the desired structured shape (dims, azimuthal, longitudinal).
We then build the model by calling the build method. When we set scaling to true we ensure that the statistical models have the
same mean inlet diameter as the original areteries. To obtain the explained variance we can call the `explained_variance` method of the model

.. code-block:: Python

   print("the fraction of explained variance is:", model.explained_variance())

to generate a new shape we supply the modes to the models `generateShape` method

.. code-block:: Python

   p = pv.BackgroundPlotter()
   shape = model.generateShape([0, -1, 0])
   mesh = pv.StructuredGrid(*shape)
   p.add_mesh(mesh)
   p.show()

   p = pv.BackgroundPlotter()
   shape = model.generateShape([3, 2.5, -2, -2, 0.1, 2,1,3,1,3,1,2])
   mesh = pv.StructuredGrid(*shape)
   p.add_mesh(mesh)
   p.show()
