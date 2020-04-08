import matplotlib as mp
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from pymethods import math


def is_ax_3d(ax) -> bool:
    """is_ax_3d

    check whether axis is 3d

    Args:
        ax

    Returns:
        bool:
    """

    if hasattr(ax, 'get_zlim'):
        return True
    else:
        return False


def is_gca_3d() -> bool:
    """check_if_gca_is_3d_axis

    check if current global axis is 3d

    Returns:
        bool: true or false whether or not the axis is in 3d
    """

    if len(mp.pyplot.get_fignums()) > 0:
        if is_ax_3d(mp.pyplot.gca()):
            return True
        return False
    else:
        return False


def figure_3d():
    """figure_3d

    create a 3d figure and axis

    Returns:
        typing.Tuple[plt.figure.Figure, plt.axis.Axis]: [description]
    """

    fig = mp.pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')
    return fig, ax


def gcfa3d():
    """gcfa3d [

        get the current 3d figure and axes

    Returns:
        typing.Tuple[plt.figure.Figure, plt.axis.Axis]:
    """

    openFigs = mp._pylab_helpers.Gcf.get_all_fig_managers()
    if len(openFigs) == 0:
        f, ax = figure_3d()
        return f, ax
    else:
        f = mp.pyplot.gcf()
        ax = f.axes
        if len(ax) == 1:
            ax = ax[-1]

        if is_ax_3d(ax):
            return f, ax
        else:
            f, ax = figure_3d()
            return f, ax


def equal_aspect_3d(*args) -> None:
    """approximate equal aspect for 3d axis
    """
    if len(args) == 0:
        f, ax = gcfa3d()
    else:
        assert len(args) == 1
        ax = args[0]
        if not is_ax_3d(ax):
            f, ax = gcfa3d()

    lims = [getattr(ax, 'get_%slim' % axis)() for axis in ['x', 'y', 'z']]
    r_max = max([np.abs(l[1]-l[0])/2 for l in lims])
    for axes, lim in zip(['x', 'y', 'z'], lims):
        mid_lim = (lim[1]+lim[0])/2
        min_max_lim = [mid_lim - r_max, mid_lim + r_max]
        getattr(ax, 'set_%slim' % axes)(min(min_max_lim), max(min_max_lim))


def equal_aspect_3d_centered(centroid: np.ndarray, ax=None) -> None:
    """equal_aspect_3d_centered

    apprimate equal aspect around a centroid

    Args:
        centroid (np.ndarray):
        ax ([type], optional): if none use gca to grab available axis.
            Defaults to None.

    Returns:
        None:
    """
    if ax is None:
        f, ax = gcfa3d()
    else:
        if not is_ax_3d(ax):
            f, ax = gcfa3d()
    centroid = np.array(centroid)
    centroid = centroid.squeeze()
    lims = [getattr(ax, 'get_%slim' % axis)() for axis in ['x', 'y', 'z']]
    r_max = max([np.abs(l[1]-l[0])/2 for l in lims])
    for axes, mid_pt in zip(['x', 'y', 'z'], centroid):
        min_max_lim = [mid_pt - r_max, mid_pt + r_max]
        getattr(ax, 'set_%slim' % axes)(min(min_max_lim), max(min_max_lim))


def quiver3d(*args, ax=None, **kwargs):
    if ax is None:
        f, ax = gcfa3d()
    else:
        if not is_ax_3d(ax):
            f, ax = gcfa3d()
    obj = ax.quiver(*args, **kwargs)
    return f, ax, obj


def scatter3d(*args, ax=None, **kwargs):
    if ax is None:
        f, ax = gcfa3d()
    else:
        if not is_ax_3d(ax):
            f, ax = gcfa3d()
    obj = ax.scatter(*args, **kwargs)
    return f, ax, obj


def plot3d(*args, ax=None, **kwargs):
    if ax is None:
        f, ax = gcfa3d()
    else:
        if not is_ax_3d(ax):
            f, ax = gcfa3d()
    obj = ax.plot(*args, **kwargs)
    return f, ax, obj


class MultiScatter:

    def __init__(self, data, color, *global_args, **kwargs):
        kwargs['alpha'] = kwargs.get('alpha', 1)
        kwargs['cmap'] = kwargs.get('cmap', 'jet')
        self.global_args = global_args
        self.kwargs = kwargs
        self.data = data
        self.color = color
        self.f = mp.pyplot.figure()

    def __call__(self, *args, interval=1, **kwargs):
        self.axes = []
        data = self.data[:, ::interval]
        for i, color in enumerate(self.color):
            color = color[::interval]

            stats = math.SummaryStatistics(color)
            name = self.name_generator(i)
            ax = self.axes_generator(i)

            self.axes.append(ax)

            self.kwargs.update(dict(
                c=color,
                vmin=stats.mu_m_2sigma,
                vmax=stats.mu_p_2sigma
            ))

            cset = ax.scatter(*data, *self.global_args, **self.kwargs)

            self.colorbar_generator(data, color, name, stats, ax, cset)

            ax.set_title(self.title_generator(name, stats))
            ax.set_xlabel('x')
            ax.set_xlabel('y')
            ax.set_xlabel('z')
            self.post_plot(ax)

        return self.f, self.axes

    def colorbar_generator(self, data, color, name, stats, ax, cset):
        data = np.array(data)
        if not np.isclose(np.sum(data - data[0]), 0):
            self.f.colorbar(cset, ax=ax)

    def title_generator(self, name, stats):
        mean_pm_std = '%0.3f $\pm$ 2x%0.3f' % (stats.mean, stats.std)
        return f'principal curvature {name}, $\mu \pm 2\sigma$={mean_pm_std}'

    def axes_generator(self, i):
        return self.f.add_subplot(121 + i, projection='3d')

    def name_generator(self, i):
        return i

    def post_plot(self, ax, centroid):
        equal_aspect_3d_centered(centroid, ax=ax)