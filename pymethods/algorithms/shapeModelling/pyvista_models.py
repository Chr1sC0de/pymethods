import pyvista as pv
from pymethods.algorithms.shapeModelling import PointDistributionModel
from pymethods.arrays import Pointsurface, Contour
import numpy as np
import matplotlib.pyplot as plt

class PyVistaPointDistributionModel(PointDistributionModel):

    def __init__(self, *args, structured_shape=None, **kwargs):
        self.structured_shape = structured_shape
        super().__init__(*args, **kwargs)

    def _shapeLoader(self):
        readable = pv.READERS.keys()
        shapes = [
            np.array(pv.read(file).points.T)
            for file in self.dataPath.glob('*.vtk')
            if file.suffix in readable]

        return shapes

    def postProcessGenerated(self, shape):
        if self.structured_shape is not None:
            shape = shape.reshape(self.structured_shape, order='F')
        return shape

class CylindricalPointModel(PyVistaPointDistributionModel):

    def __init__(self, *args, structured_shape, **kwargs):
        self.structured_shape = structured_shape
        assert self.structured_shape is not None
        super().__init__(*args, structured_shape=structured_shape, **kwargs)

    def _shapePreprocess(self, shapes):

        re_structured_shapes = [
            shape.reshape(self.structured_shape, order='F')
            for shape in shapes
        ]

        inlets = [
            Contour(shape[:, :, 0]) for shape in re_structured_shapes
        ]
        areas = [inlet.area for inlet in inlets]
        diameters = [np.sqrt(area/np.pi)*2 for area in areas]

        self.meanOriginalDiameters = np.mean(diameters)

        return shapes


    def postProcessGenerated(self, shape):
        shape = shape.reshape(self.structured_shape, order='F')

        shape = np.concatenate([shape, shape[:,0,None,:]], axis=1)
        return shape

    def postProcessBuilt(self, shapes, scale=False):
        if scale:
            re_structured_shapes = [
                shape.reshape(self.structured_shape, order='F')
                for shape in shapes
            ]
            inlets = [
                Contour(shape[:, :, 0]) for shape in re_structured_shapes
            ]
            areas = [inlet.area for inlet in inlets]
            diameters = [np.sqrt(area/np.pi)*2 for area in areas]
            self.meanAlignedDiameters = np.mean(diameters)
            self.scaleFactor = self.meanOriginalDiameters / self.meanAlignedDiameters
        return shapes

if __name__ == "__main__":
    import pymethods
    model = CylindricalPointModel(
        r'D:\Github\statisticalShapeModel\__AngioLADSurfaces\VTKS', structured_shape=(3, 360, 720))
    model.build(scale=True, modes=10)
    shape = model.generateShape([0, -10, 0])
    shape = pv.StructuredGrid(*shape)
    shape.plot()



