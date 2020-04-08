from pymethods.algorithms.transfinite_interpolation import Transfinite2d
from pymethods.arrays import Contour, Vectorspace
from pymethods.arrays.structured import CylindricalSurface
import numpy as np
import pyvista as pv


class TransfiniteCylinder:
    def __init__(self, cylindrical_surface):
        assert isinstance(cylindrical_surface, CylindricalSurface)
        self._cylindrical_surface = cylindrical_surface

    def __call__(self, u, v, w, reparam=True):

        pts_contours_original = np.linspace(
            0, 1, self._cylindrical_surface.shape[1]
        )
        surface = self._cylindrical_surface(pts_contours_original, w, reparam=reparam)

        surface = np.stack([
            Transfinite2d(Contour(surface[:, :, i]))(u, v) for i in range(surface.shape[-1])
        ], axis=-1)

        return surface

    def pts_mesh(self, u, v, w, **kwargs):
        UU, VV = np.meshgrid(u, v)
        UU = UU.flatten()
        VV = VV.flatten()
        return self(UU, VV, w, **kwargs).reshape(
            (3, len(u), len(v), len(w))
        )

    def pts_mesh_column(self, u, v, w):
        return Vectorspace(self.pts_mesh(u, v, w).reshape(
            3,-1
        ))

    def mesh_vtk(self, u, v, w):
        return pv.StructuredGrid(
            *self.pts_mesh(u, v, w)
        )


