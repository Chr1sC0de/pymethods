import numpy as np
from pathlib import Path
import pymethods as py
import abc
import scipy
from scipy.stats import linregress
import logging

class _svdDescriptor:
    def __init__(self, key):
        self.key = key

    def __get__(self, obj, objType):
        if not hasattr(obj, self.key):
            raise Exception(
                'run.ndshape.svd'
            )
        else:
            return getattr(obj, self.key)


class PointDistributionModel(abc.ABC):
    # http://people.ee.ethz.ch/~cattin/MIA-ETH/pdf/MIA-10-SSM.pdf

    def __init__(self, dataPath):
        self.dataPath = Path(dataPath)

    def objectiveFunction(self, listShapes):
        difference = self.meanShape - np.array(listShapes)
        r = np.linalg.norm(difference, axis=1)
        return np.mean(np.mean(r, axis=-1))

    @abc.abstractmethod
    def _shapeLoader(self):
        NotImplemented
        shapes = None
        # white method to extract shapes here
        return shapes

    def _shapePreprocess(self, surfaces):
        return surfaces

    def _postProcessBuiltHook(self, surfaces):
        pass

    def postProcessBuilt(self, shapes, scale=False):
        return shapes

    def postProcessGenerated(self, shape):
        return shape

    def alignShapesToMean(self, shapeList, scale=False):
        alignedShapes = []

        for shape in shapeList:
            if hasattr(self, "meanShape"):
                alignedShape = py.math.rigid_transform(shape, self.meanShape)

                if scale:
                    slope, intercept, r_value, p_value, std_err = \
                        linregress(alignedShape.flatten(), self.meanShape.flatten())
                    alignedShape = alignedShape*slope + intercept

                alignedShapes.append(
                    alignedShape
                )
            else:
                raise Exception(
                    "No mean shape detected, run build"
                )
        return alignedShapes

    def build(
            self, modes=10, eps=10**(-5), countCap=1000, costlimit=0,
            scale=False, startShape=None
        ):
        self.scaleFactor = 1
        shapes = self._shapeLoader()
        shapes = self._shapePreprocess(shapes)
        # calculate the true mean inlet area
        self._postProcessBuiltHook(shapes)
        # center each shape
        centeredShapes = [surface - surface.mean(1, keepdims=True)
                          for surface in shapes]
        if startShape == None:
            firstInd = np.random.randint(len(centeredShapes))
        else:
            firstInd = startShape
        # set the randomly selected shape to the meanshape
        self.meanShape = centeredShapes[firstInd]
        # align the shapes to the selected mean shape
        alignedShapes = self.alignShapesToMean(centeredShapes, scale=scale)
        # current cost
        cost = self.objectiveFunction(alignedShapes)
        # set the intial mean shape
        self.meanShape = np.array(alignedShapes).mean(axis=0)
        self.meanShape = self.meanShape - self.meanShape.mean(
            axis=-1, keepdims=True)
        # eps to stop iterations
        count = 0
        while True:
            # realign the shapes
            alignedShapes = self.alignShapesToMean(alignedShapes)
            # assign the new meanShape
            self.meanShape = np.array(alignedShapes).mean(axis=0)
            self.meanShape = self.meanShape-self.meanShape.mean(
                axis=-1, keepdims=True)
            newcost = self.objectiveFunction(alignedShapes)
            if np.abs(cost-newcost) < eps:
                break
            else:
                cost = newcost
                logging.info("The current cost is %0.3f"%cost)
            if count > countCap:
                break
            if cost < costlimit:
                break
            count += 1
        self.alignedShapes = self.postProcessBuilt(alignedShapes, scale=scale)
        self.ndspace = self.NDSpace(self.meanShape, self.alignedShapes)
        self.ndspace.svd(modes=modes)

    class NDSpace:

        U = _svdDescriptor("_U")
        V_T = _svdDescriptor("_V_T")
        W = _svdDescriptor("_W")

        def __init__(self, meanShape, alignedShapes):
            self.originalShape = meanShape.shape
            self.meanShape = meanShape.flatten('F')
            self.alignedShapes = [
                shape.flatten('F') for shape in alignedShapes]
            self.pointDistribution = np.stack(
                self.alignedShapes, axis=-1
            )
            self.pointDeformation = \
                self.pointDistribution - self.pointDistribution.mean(
                    -1, keepdims=True)

        def explained_variance(self):
            return self._explained_variance

        def svd(self, modes=6):
            self.mode = modes
            self._U, self._W, self._V_T = scipy.sparse.linalg.svds(
                self.pointDeformation, k=(np.min(self.pointDeformation.shape)-1))
            indices = np.flipud(np.argsort(self._W))
            self._U = self._U[:, indices]
            self._W = self._W[indices]
            self._V_T = self.V_T[indices, :]

            self._explained_variance = np.sum(self._W[0:modes])/np.sum(self._W)

            self._U = self._U[:, 0:modes]
            self._W = self._W[0:modes]
            self._V_T = self._V_T[0:modes, :]

        def recoverDimensions(self, shape):
            return shape.reshape(
                self.originalShape, order='F'
            )

    def explained_variance(self):
        return self.ndspace.explained_variance()

    def generateShape(self, C):
        combination = 0
        tmp = np.zeros(len(self.ndspace.U))
        tmp[0:len(C)] = C
        C = tmp
        for w, U_T, c in zip(self.ndspace.W, self.ndspace.U.T, C):
            combination += np.sqrt(w)*c*U_T
        newshape = self.ndspace.meanShape + combination
        newshape = self.ndspace.recoverDimensions(newshape) * self.scaleFactor
        newshape = self.postProcessGenerated(newshape)
        return newshape

    def recommendedAmountModes(self, explainedVarReq=0.8):
        explainedVar = 0
        count = 0
        while explainedVar < explainedVarReq:
            count += 1
            explainedVar = \
                np.sum(self.ndspace.W[0:count])/np.sum(self.ndspace.W)
        return count