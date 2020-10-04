import numpy as np
try:
    from pymethods.arrays import Vector, Angle
    from pymethods import math, utils
except ImportError:
    from .Vector import Vector
    from .. import math
    from .. import utils
    from .Angle import Angle
import typing
import logging
_is_subset_degrees = utils.IsSubsetString('degrees')
import pyvista as pv


class Basis(Vector):
    normal = utils.NoInputFunctionAlias('calc_normal', store=False)

    def __array_finalize__(self, obj):
        if obj is None:
            return None
        else:
            if len(self.shape) == 1:
                self.__class__ = Vector
            # try
            # elif self.shape[-1] == 1:
            #     self.__class__ = Vector

    def make_3d(self):
        if self.shape[0] < 3:
            return self.__class__(math.make_3d(self))
        elif self.shape[0] > 3:
            logging.info("dimensions are greater than 3 cannot convert to 3d")

    def rotate(self, phi, units='radians'):
        normal = self.calc_normal()
        if _is_subset_degrees(units):
            phi = Angle.deg_to_rad(phi)
        R = math.rotation_matrix(normal, phi)
        return R @ self

    def skew_symmetric(self):
        dims, n_pts = self.shape
        output = np.zeros((n_pts, dims, dims))
        for i, vector in enumerate(self.T):
            output[i, :] = math.skew_symmetric_3d(vector)
        return output.squeeze()

    def calc_normal(self):
        return self[:, -1]

    @classmethod
    def identity(cls, n_dims=3) -> object:
        return cls(np.eye(n_dims))

    @classmethod
    def _parse_single_arg(cls, array: np.ndarray) -> np.ndarray:
        assert utils.len_shape(array) == 2, \
            "The lenshape of the input must be 2"
        assert array.shape[0] == 3, \
            "expecting input of dimension 3x3"
        assert array.shape[1] == 3, \
            "expecting input of dimension 3x3"
        array = np.asarray(array)
        return array

    @classmethod
    def _parse_star_arg(
            cls, args: typing.Iterable[typing.Iterable]) -> np.ndarray:
        assert len(args) == 3,  \
            f"expected 3 arguments for {cls}"
        return np.stack(
            args, axis=-1
        )

    @classmethod
    def _new_hook_post_parse(self, out):
        out = math.normalize(out)
        # if math.is_linearly_dependent(out):
        #     logging.debug("supplied vectors are not linearly independent.\
        #         Approximating a linearly independent basis")
        #     out = math.make_linearly_independent(out)
        return out

    def quiverly(self, *args, **kwargs
                 ):
        for i, vector in enumerate(self.T):
            if i == 0:
                f = None
            elif not kwargs.get('fig', None) is None:
                f = kwargs['fig']
            f, o = vector.quiverly(
                fig=f, **kwargs
            )
        return f, o

    def to_vtk(self, method='pyvista', origins=None):
        if method == "pyvista":
            if origins == None:
                output = pv.PolyData(np.zeros_like(self).T)
                output.vectors = self.T
            else:
                if origins is None:
                    origins = np.zeros_like(self)
                origins = np.array(origins).squeeze()
                if len(origins.shape) == 1:
                    origins = np.ones_like(self) * origins[:, None]
                    output = pv.PolyData(origins.T)
                else:
                    assert np.allclose(origins.shape,self.shape), \
                        "Origins must have the same shape as self"
                    output = pv.PolyData(origins.T)
                output.vectors = self.T
            return output



if __name__ == "__main__":
    basis = Basis(
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    )

    basis.quiverly()
    f.show()