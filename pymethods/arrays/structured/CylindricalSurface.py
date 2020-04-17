import numpy as np
import logging
try:
    from pymethods.arrays import FlatContour, Curve, Contour, ColumnVector
    from pymethods import math
    from pymethods.algorithms import write_stl
    import pymethods as pma
except ImportError:
    from ...arrays import FlatContour, Curve, Pointsurface
    from ... import math
    from ...algorithms import write_stl

from tqdm import tqdm
import pyvista as pv

logger = logging.getLogger().setLevel(logging.INFO)


class CylindricalSurface(np.ndarray):

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            out = np.array(args).view(cls).squeeze()
            assert len(out.shape) == 3
            return out

        if len(args) > 1:
            return np.stack(args, axis=-1)

    def __call__(self, U, V, close=True, reparam=True):
        centroids = np.concatenate([Contour(self[:,:, i]).centroid for i in range(self.shape[-1])], axis=-1)
        centerline = Curve(centroids)
        if reparam:
            centerline_s = centerline.s_frac
        else:
            centerline_s = None

        surface = np.stack(
            [Curve(self[:, i, :], reparam_curve=centerline_s)(V) for i in  range(self.shape[1])],
            axis=1
        )
        if any([U[-1] != 1, U[0] != 0]):
            surface = np.stack(
                    [Curve(surface[:, :, i])(U) for i in  range(surface.shape[-1])],
                axis=-1
            )
        else:
            surface = np.stack(
                    [FlatContour(surface[:, :, i])(U) for i in  range(surface.shape[-1])],
                axis=-1
            )

        return self.__class__(surface)

    def interpolate_long(self, npts, *args, centerline_reparam=False, **kwargs):
        newsurface = np.zeros(
            (self.shape[0], self.shape[1], npts)
        )
        if centerline_reparam:
            centroids = np.concatenate([Contour(self[:,:, i]).centroid for i in range(self.shape[-1])], axis=-1)
            centerline = Curve(centroids)
            centerline_s = centerline.s_frac

        for i in range(self.shape[1]):
            line = Curve(self[:, i, :], **kwargs)

            if not centerline_reparam:
                newsurface[:, i, :] = line(
                        np.linspace(0, 1, npts)
                    )
            else:
                newsurface[:, i, :] = line(
                        np.linspace(0, 1, npts), reparam_curve=centerline_s
                )
        return self.__class__(newsurface)

    def interpolate_contours(self, npts, *args, **kwargs):
        newsurface = np.zeros(
            (self.shape[0], npts, self.shape[-1])
        )
        for i in range(self.shape[-1]):
            line = FlatContour(self[:, :, i], **kwargs)
            newsurface[:, :, i] = line(
                    np.linspace(0, 1, npts)
                )
        return self.__class__(newsurface)

    def align_contour_points(self, progress=False):
        if isinstance(self, (list, tuple)):
            contour_stack = np.stack(self, axis=-1)
        else:
            contour_stack = self

        converged = False
        shortest_length = np.inf

        while not converged:

            for i in tqdm(
                    np.arange(contour_stack.shape[-1]-1), disable=not progress):
                A = contour_stack[:, 0, i, None]
                B = contour_stack[:, :, i+1]
                distance = math.l2_norm(B-A)
                argmin = np.argmin(distance.squeeze())
                contour_stack[:, :, i+1] = np.roll(B, -argmin, axis=-1)

            # find the shortest path
            deltas = contour_stack[:, :, 1:] - contour_stack[:, :, 0:-1]
            deltas = np.linalg.norm(deltas, axis=0)
            all_lengths = deltas.sum(-1)
            i_short = np.argmin(all_lengths)
            current_shortest = all_lengths[i_short]
            if shortest_length > current_shortest:
                shortest_length = current_shortest
            else:
                break
            contour_stack = np.roll(contour_stack, -i_short, axis=1)
            logging.debug(
                'rollval=%d, shortest_length=%0.3f' % (
                    i_short, shortest_length))

        # now find the shortest path and make that into the cutline
        return CylindricalSurface(contour_stack)

    def filter(self, retries=10, **kwargs):
        tries = []
        roll_vals = np.linspace(
            0, self.shape[1], retries
        )
        for roll in roll_vals:
            rolled = np.roll(self, int(roll), 1)
            filtered = math.filters.sgolay2d(
                rolled, padding='periodic_replication', **kwargs)
            unrolled = np.roll(filtered, -int(roll), 1)

            tries.append(unrolled)

        return self.__class__(
            np.mean(tries, 0)
        )

    @classmethod
    def from_contours(cls, contours):
        return cls(cls.align_contour_points(contours))

    def to_vtk(self, method='pyvista'):
        if method == 'pyvista':
            return pv.StructuredGrid(*self)

    def to_stl(self, path="mesh.stl"):
        write_stl(self, path)

    def scatter3d(self, *args, **kwargs):
        color = kwargs.pop('color', 'blue')
        long = self.shape[-1]
        for i in range(long):
            f, ax, obj = Curve.scatter3d(
                self[:, :, i], *args, color=color, **kwargs)
        return f, ax, obj

    def plot3d(self, *args, **kwargs):
        color = kwargs.pop('color', 'blue')
        long = self.shape[-1]
        for i in range(long):
            f, ax, obj = Curve.plot3d(
                self[:, :, i], *args, color=color, **kwargs)
        return f, ax, obj

    def toColumnSurface(self, external=True, **kwargs):
        psurface = pma.arrays.Pointsurface(
            self.reshape(3, -1), external=True, **kwargs)
        return psurface

    def calculate_normals(
            self, external=True, leafsize=200, neighbours=50,
            log=True, return_psurf=False, **kwargs):
        shape = self.shape
        surface_list = self.reshape(3, -1)
        psurface = pma.arrays.Pointsurface(
            surface_list, external=True, leafsize=leafsize,
            neighbours=neighbours, log=log)
        normals = psurface.compute_all_normals()
        if return_psurf:
            return (
                normals.reshape(normals.shape[0], shape[-2], shape[-1]),
                psurface
            )
        else:
            return normals.reshape(normals.shape[0], shape[-2], shape[-1])

    def get_centerline(self):
        centroids = np.concatenate([Contour(self[:,:, i]).centroid for i in range(self.shape[-1])], axis=-1)
        centerline = Curve(centroids)
        return centerline


if __name__ == "__main__":
    import sys
    import pymethods as pma
    import pymethods.pyplot as plt
    import pathlib as pt
    import numpy as np
    path_angio = pt.Path(r'D:\Github\pymethods\testsReconstruction\test_1\angiography')
    folder_angio = pma.parse.angiography.Folder(path_angio)

    cross_sections = folder_angio.CrossSectionEllipseSet1.data

    surface = CylindricalSurface.from_contours(cross_sections)

    surface = surface.filter()

    surface.calculate_normals()

    plt.scatter3d(
        *surface
    )

    plt.show()

    surface = surface.interpolate_long(720, k=3)
    surface = surface.interpolate_contours(360, k=3)
    surface = surface.align_contour_points()
    surface = surface.filter(window_size=13)
    surface = surface.filter(window_size=15)
    surface = surface.filter(window_size=43)

    surface.to_vtk().plot()

