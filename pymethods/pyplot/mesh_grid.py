from .. import pyplot as plt


def plot_grid2d(grid, *args, ax=None, boundaries_on=False, **kwargs):

    _, rows, cols = grid.shape

    if ax is None:
        ax = plt.gca()

    if boundaries_on:

        for i in range(rows):
            ax.plot(*grid[:2, i, :], *args, **kwargs)

        for i in range(cols):
            ax.plot(*grid[:2, :, i], *args, **kwargs)

    else:

        for i in range(1, rows-1):
            ax.plot(*grid[:2, i, :], *args, **kwargs)

        for i in range(1, cols-1):
            ax.plot(*grid[:2, :, i], *args, **kwargs)

    return ax


def plot_grid3d(grid, *args, ax=None, boundaries_on=False, **kwargs):

    _, rows, cols = grid.shape

    if ax is None:
        _, ax = plt.gcfa3d()

    if boundaries_on:

        for i in range(rows):
            plt.plot3d(*grid[:, i, :], *args, ax=ax, **kwargs)

        for i in range(cols):
            plt.plot3d(*grid[:, :, i], *args, ax=ax, **kwargs)

    else:

        for i in range(1, rows-1):
            plt.plot3d(*grid[:, i, :], *args, ax=ax, **kwargs)

        for i in range(1, cols-1):
            plt.plot3d(*grid[:, :, i], *args, ax=ax, **kwargs)

    return ax