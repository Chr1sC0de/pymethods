import numpy as np
from typing import Union, Iterable

try:
    from pymethods import math, utils, pyplot
    from pymethods.arrays import Angle
except ImportError:
    from .. import math, pyplot
    from ..arrays import Angle
    from .. import utils

import logging

class Array(np.ndarray):
    pass


class Vector(np.ndarray):
    bar = utils.NoInputFunctionAlias('magnitude', store=True)
    hat = utils.NoInputFunctionAlias('normalize', store=True)
    _x = utils.NoInputFunctionAlias('skew_symmetric', store=True)
    column = utils.NoInputFunctionAlias('make_column', store=False)

    xyScaleUnits = True

    @classmethod
    def _parse_single_arg(cls, out):
        return np.array(out)

    @classmethod
    def _parse_star_arg(cls, args):
        return np.stack(args, axis=0)

    @classmethod
    def _new_hook_post_parse(cls, out):
        return out

    def __new__(
            cls, *args, column=False, **kwargs: dict) -> object:
        """__new__

        Vector object creation
        Args:
            *args: args is a variable argument. It
                can either be an iterable or a
                tuple containing a single list. i.e. a
                Vectors object can be instantiated
                eiter by V = Vector(1, 2, 3) or
                V = Vector([1, 2, 3])
        Returns:
            Vector: [description]
        """

        if len(args) == 1:
            if isinstance(args[0], Iterable):
                out = cls._parse_single_arg(args[0])
            else:
                raise ValueError(f"input must {Iterable}")
        else:
            out = cls._parse_star_arg(args)

        out = cls._new_hook_post_parse(out)

        if column:
            if len(out.shape) == 1:
                out = out[:, None]

        return out.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return None
        else:
            if len(self.shape) == 2:
                if self.shape[-1] > 1:
                    self.__class__ = Array

    def make_3d(self):
        if self.shape[0] < 3:
            return self.__class__(math.make_3d(self))
        elif self.shape[0] > 3:
            logging.info("dimensions are greater than 3 cannot convert to 3d")
        return self

    def rotation_matrix(self, phi: np.float, units='radians') -> np.ndarray:
        """rotation_matrix

        get the rotation matrix for angle phi around self

        Args:
            phi (np.float): rotation angle in units
            units (str, optional): ['radians' or 'degrees'].
                Defaults to 'radians'.

        Returns:
            np.ndarray: Rotation matrix
        """
        phi = Angle(phi, units=units).rad
        return math.rotation_matrix(self, phi)

    def direct_vector(self, vector: np.ndarray) -> np.ndarray:
        """direct_vector

        Point the current vector in the same direction as a secondary vector

        Args:
            vector (np.ndarray): vector to point in the same direction to

        Returns:
            np.ndarray: re-oriented vector
        """
        self_project = math.vector_project(self, vector)

        pos_dist = math.l2_norm(vector - self_project)
        neg_dist = math.l2_norm(-vector - self_project)

        if neg_dist < pos_dist:
            return -1 * self
        else:
            return self

    def rotate_around_vector(
            self, vector: np.ndarray,
            phi: np.float, units='radians') -> np.ndarray:
        phi = Angle(phi, units=units).rad
        R = math.rotation_matrix(vector, phi)
        return R @ self

    def make_column(self):
        if utils.len_shape(self) == 1:
            return self[:, None]
        return self

    def normalize(self):
        return math.normalize(self)

    def magnitude(self):
        return math.l2_norm(self).squeeze()

    def scalar_project(self, vector: np.ndarray) -> np.ndarray:
        projected = math.scalar_project(self, vector)
        return projected

    def vector_project(self, vector: np.ndarray) -> np.ndarray:
        return math.vector_project(self, vector)

    def perpendicular(self, vector: np.ndarray) -> np.ndarray:
        return math.vector_perpendicular(self, vector)

    def project_to_plane(self, normal: np.ndarray) -> np.ndarray:
        return self.__class__(math.project_to_plane(self, normal))

    def change_reference_frame(self, basis: np.ndarray) -> np.ndarray:
        return self.scalar_project(basis)

    def dot(self, basis: np.ndarray) -> Union[np.ndarray, np.float]:
        return math.dot(self, basis)

    def cross(self, vector: np.ndarray) -> np.ndarray:
        return math.cross(self, vector)

    def angle(self, vector: np.ndarray) -> Union[np.ndarray, np.float]:
        return Angle(math.smallest_angle_between_vectors(self, vector))

    def directed_angle(
            self, vector: np.ndarray,
            direction: np.ndarray) -> Union[np.ndarray, np.float]:
        return Angle(math.directed_angle(self, vector, direction))

    def skew_symmetric(self):
        return math.skew_symmetric_3d(self)

    def as_numpy(self):
        return self.view(np.ndarray)

    # ----------- PLOTTING FUNCTIONS ------------------------------------------

    def quiverly(
            self, *args,
            fig=None, showarrow=True, color="black", scale=5, origin=None,
            arrow_size='scaled', line_kwargs=None, name='Vector',
            showlegend=False
            ):

        if origin is None:
            origin = np.zeros(3)

        assert isinstance(self, Vector)

        import plotly.graph_objs as go
        x = np.stack([0, self[0].squeeze()]) + origin[0]
        y = np.stack([0, self[1].squeeze()]) + origin[1]

        color_scale = [[0, color], [1, color]]

        if fig is None:
            fig = go.Figure()

        if len(self) == 2:
            z = np.zeros_like(x) + origin[2]
        else:
            z = np.stack([0, self[2].squeeze()]) + origin[2]

        if arrow_size == 'scaled':
            u = [(x[1]-x[0])/scale]
            v = [(y[1]-y[0])/scale]
            w = [(z[1]-z[0])/scale]
        elif isinstance(arrow_size, (int, float)):
            du = (x[1]-x[0])
            dv = (y[1]-y[0])
            dz = (z[1]-z[0])
            mag_du = np.sqrt(du**2 + dv**2 + dz**2)
            u = [du/mag_du*arrow_size]
            v = [dv/mag_du*arrow_size]
            w = [dz/mag_du*arrow_size]
        else:
            raise Exception(
                "size must either be set to scaled or an int or float")

        obj = go.Scatter3d(
            x=x, y=y, z=z,
            marker=dict(size=0),
            line=dict(color=color),
            name=name,
            showlegend=showlegend
        )

        cone = go.Cone(
           x=[x[1]], y=[y[1]], z=[z[1]],
           u=u, v=v, w=w,
           colorscale=color_scale,
           showscale=False,
           name=None
        )

        fig.add_trace(obj)
        fig.add_trace(cone)
        return fig, obj

    def scatterly(
            self, *args, fig=None, color="black", showlegend=False, **kwargs):

        import plotly.graph_objs as go

        if fig is None:
            fig = go.Figure()

        x = self[0].squeeze()
        y = self[1].squeeze()

        if len(self) == 2:
            z = 0*np.zeros_like(0)
        else:
            z = self[2].squeeze()

        base_kwargs = {
            'xlim': (x.min()*1.5, x.max()*1.5),
            'ylim': (y.min()*1.5, y.max()*1.5),
            'zlim': (z.min()*1.5, z.max()*1.5)
        }

        base_kwargs.update(kwargs)

        obj = go.Scatter3d(
            x=[x], y=[y], z=[z],
            showlegend=showlegend,
            # **base_kwargs
        )

        fig.add_trace(obj)
        return fig, obj

    def scatter3d(self, *args, **kwargs):
        return pyplot.scatter3d(*self, *args, **kwargs)

    def scatter2d(self, *args, **kwargs):
        return pyplot.scatter(*self[0:2], *args, **kwargs)

    def quiver2d(self, *args, origin=None, **kwargs):
        if origin is None:
            origin = np.zeros_like(self)
        else:
            origin = np.squeeze(origin)[:, None] * np.ones_like(self)
        obj = pyplot.quiver(*origin[0:2], *self[0:2], *args, **kwargs)
        pyplot.gca().scatter(*origin[0:2], alpha=0)
        pyplot.gca().scatter(*(self[0:2].squeeze()+origin[0:2]), alpha=0)
        return pyplot.gcf(), pyplot.gca(), obj

    def plot3d(self, *args, **kwargs):
        return pyplot.plot3d(*self, *args, **kwargs)

    def quiver3d(self, *args, origin=None, **kwargs):
        if origin is None:
            origin = np.zeros_like(self)
        else:
            origin = np.squeeze(origin)[:, None] * np.ones_like(self)
        f, ax, obj = pyplot.quiver3d(*origin, *self, *args, **kwargs)
        ax.scatter(*origin, alpha=0)
        ax.scatter(*(self.squeeze()+origin), alpha=0)
        return f, ax, obj

    def to_vtk(self, method='pyvista', origin=[0,0,0]):
        if method == 'pyvista':
            output = pv.PolyData(origin)
            output.vector = self.T
            return output


class ColumnVector(Vector):
    def __new__(cls, *args, **kwargs: dict) -> object:
        return super(ColumnVector, cls).__new__(
            cls, *args, column=True, **kwargs)


if __name__ == "__main__":
    V = Vector(1, 2, 3)
    V.quiver3d()
    import matplotlib.pyplot as plt
    plt.show()