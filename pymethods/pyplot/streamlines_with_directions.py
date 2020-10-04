import pymethods as pma
import numpy as np


_quiver_kwargs_names_3d = [
    "units",
    "angles",
    "scale",
    "scale_units",
    "width",
    "headwidth",
    "minshaft",
    "minlength",
    "pivot",
    "arrow_length_ratio"
]


def plot_stream3d(*all_data, ax=None, loc=0.9 , mag=0.1, **kwargs):

    if ax is None:
        ax = pma.pyplot.gca()

    quiver_kwargs = {
        key: kwargs.pop(key) for key in _quiver_kwargs_names_3d
        if key in kwargs.keys()
    }

    if "color" in kwargs.keys():
        quiver_kwargs["color"] = kwargs["color"]

    loc = np.array((loc))

    for i, data in enumerate(all_data):

        curve = pma.arrays.Curve(data)
        mag   = curve.s_tot * mag
        n     = int(curve.shape[-1] * loc)

        if i == 0:
            tail_tangent = pma.arrays.Vector(curve.transport_frames()[n, :, -1])
            tail_tangent = tail_tangent * mag

        curve.plot3d(ax=ax, **kwargs)

        tail_tangent.quiver3d(origin=curve(loc), ax=ax, **quiver_kwargs)


_quiver_kwargs_names = [
    "units",
    "angles",
    "scale",
    "scale_units",
    "width",
    "headwidth",
    "minshaft",
    "minlength",
    "pivot",
]

def plot_stream2d(*all_data, ax=None, loc=0.9 , mag=0.1, **kwargs):

    if ax is None:
        ax = pma.pyplot.gca()

    quiver_kwargs = {
        key: kwargs.pop(key) for key in _quiver_kwargs_names
        if key in kwargs.keys()
    }

    if "color" in kwargs.keys():
        quiver_kwargs["color"] = kwargs["color"]

    loc = np.array((loc))

    for data in all_data:

        curve = pma.arrays.Curve(data)
        mag   = curve.s_tot * mag

        n = int(curve.shape[-1] * loc)

        tail_tangent = pma.arrays.Vector(curve.transport_frames()[n, :, -1])
        tail_tangent *= mag

        ax.plot(*curve[:2], **kwargs)

        ax.quiver(*curve(loc)[:2], *tail_tangent[:2], **quiver_kwargs)
