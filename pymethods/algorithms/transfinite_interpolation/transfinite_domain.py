from pymethods.arrays import Contour, Curve, Vectorspace
import pyvista as pv
import numpy as np


class TransfiniteDomain:

    def __init__(self, c_1, c_4, c_3, c_2):

        p_12 = c_1[:, 0, None]
        p_34 = c_3[:, -1, None]
        p_14 = c_1[:, -1, None]
        p_32 = c_2[:, -1, None]

        def interpolator(u, v):
            plus = (1-v) * c_1(u) + v * c_3(u) + (1 - u) * c_2(v) + u * c_4(v)

            minus = (1-u)*(1-v) * p_12 + u*v*p_34 + u*(1-v)*p_14 + (1-u)*v*p_32

            return plus.squeeze() - minus.squeeze()

        self._interpolator = interpolator

    def __call__(self, U, V):
        return Vectorspace(self._interpolator(U, V))

    def pts_mesh_column(self, U, V, return_params=False):

        UU, VV = np.meshgrid(U, V)

        UU = UU.flatten()
        VV = VV.flatten()
        if return_params:
            return self(UU, VV), (UU, VV)
        else:
            return self(UU, VV)

    def pts_mesh_column_uniform(self, npts_U, npts_V, **kwargs):
        return self.pts_mesh_column(
            np.linspace(0, 1, npts_U),
            np.linspace(0, 1, npts_V), **kwargs
        )

    def pts_mesh(self, U, V, **kwargs):
        n_x = len(U)
        n_y = len(V)
        if kwargs.get('return_params', False):
            output = self.pts_mesh_column(U, V, **kwargs)
            return output[0].reshape(3, n_x, n_y), (
                output[1][0].reshape(n_x, n_y),
                output[1][1].reshape(n_x, n_y)
            )
        else:
            return self.pts_mesh_column(U, V, **kwargs).reshape(3, n_x, n_y)

    def pts_mesh_uniform(self, npts_U, npts_V, **kwargs):
        '''
        create a parameterized mesh with the specified number of points per axes,
        equally spaced along the square domain
        '''
        return self.pts_mesh(
            np.linspace(0, 1, npts_U),
            np.linspace(0, 1, npts_V), **kwargs
        )

    def mesh_vtk(self, U, V):
        return pv.StructuredGrid(
            *self.pts_mesh(U, V)
        )

    def mesh_uniform(self, npts_U, npts_V):
        return pv.StructuredGrid(
            *self.pts_mesh_uniform(npts_U, npts_V)
        )

