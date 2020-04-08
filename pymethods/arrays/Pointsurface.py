try:
    from pymethods import (arrays, utils, pyplot, math, algorithms)
except ImportError:
    from .. import arrays, utils, pyplot, math, algorithms
import pyvista as pv
from scipy.spatial import cKDTree
import numpy as np
import multiprocessing
from functools import wraps
import logging
_n_cpus = multiprocessing.cpu_count()

_debug_ = False

if _debug_:
    show_tqdm = True
else:
    show_tqdm = False


class _CurvatureMultiScatter(pyplot.MultiScatter):

    def title_generator(self, name, stats):
        mean_pm_std = '%0.3f $\pm$ 2x%0.3f' % (stats.mean, stats.std)
        return f'{name}, $\mu \pm 2\sigma$={mean_pm_std}'

    def name_generator(self, i):
        return f'$\kappa_{i+1}$'

    def post_plot(self, ax):
        pyplot.equal_aspect_3d_centered(self.data.mean(axis=-1), ax=ax)


class _CurvatureMultiScatterError(pyplot.MultiScatter):

    def title_generator(self, name, stats):
        mean_pm_std = '%0.3f $\pm$ 2x%0.3f' % (stats.mean, stats.std)
        return f'{name}, $\mu \pm 2\sigma$={mean_pm_std}'

    def name_generator(self, i):
        math_title = r'2 * \dfrac{ |pred-true| }{pred+true}'
        return f'${math_title}_{i+1}$'

    def post_plot(self, ax):
        pyplot.equal_aspect_3d_centered(self.data.mean(axis=-1), ax=ax)


class PrintMethod:
    def __init__(self, base_verbatim: str) -> None:
        self.base_verbatim = base_verbatim

    def __call__(self, function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            logging.debug(self.base_verbatim)
            output = function(obj, *args, **kwargs)
            logging.debug("completed %s" % self.base_verbatim)
            return output
        return wrapper


class AlignNormalsBFS(algorithms.BreadthFirstSearch):

    def post_vertex_query(self) -> None:
        self.main_vector = self.properties[self.queried_vertex, :, -1]

    def on_unvisited_edge(self) -> None:
        test_normal = self.properties[
            self.queried_edge_vertex, :, -1]
        pos_vect = self.main_vector-test_normal
        neg_vect = -self.main_vector-test_normal
        mag_pos = sum(pos_vect*pos_vect)
        mag_neg = sum(neg_vect*neg_vect)
        if mag_neg < mag_pos:
            self.properties[self.queried_edge_vertex] *= -1


class Pointsurface(arrays.Vectorspace):
    def __init__(
            self, *args, leafsize=200, neighbours=50,
            external=True, log=True, **kwargs) -> None:
        self.log = log
        self.leafsize = leafsize
        self.external = external
        self.n_neighbours = neighbours

    def query_nearest(self, points: np.ndarray) -> np.ndarray:
        if not hasattr(self, "kdtree"):
            self.compute_kdtree()
        points = utils.make_column(points)
        dist_indices = self.kdtree.query(points.T, k=(self.n_neighbours+1))
        if len(points.T) == len(self.T):
            self.nn_weights, self.nn_indices = dist_indices
            self.nn_weights = self.nn_weights[:, 1:]
            self.nn_indices = self.nn_indices[:, 1:]
        indices = dist_indices[1][:, 1:]
        return self.kdtree.data[indices].swapaxes(1, 2).view(np.ndarray)

    @PrintMethod("computing kdtree")
    def compute_kdtree(self) -> cKDTree:
        if not hasattr(self, 'kdtree'):
            self.kdtree = cKDTree(
                self.T, leafsize=self.leafsize)
            return self.kdtree
        else:
            return self.kdtree

    @PrintMethod("computing nearest neighbours from kdtree")
    def compute_nearest_neighbours(self) -> np.ndarray:
        points = utils.make_column(self)
        self.nearest_neighbours = self.query_nearest(points)
        return self.nearest_neighbours

    @PrintMethod("computing normals")
    def compute_all_normals(
            self) -> np.ndarray:
        self.point_basis = self.compute_point_normals(self)
        self._align_normals()
        self.point_normals = self.point_basis[:, :, -1].T
        return self.point_normals

    @PrintMethod("computing principle curvatures")
    def compute_principle_curvatures(
            self, method='can_lsq_fit', n_processors='max') -> np.ndarray:
        if not hasattr(self, 'point_basis'):
            self.compute_all_normals()
        self.principle_curvatures, self.principle_directions = \
            getattr(algorithms.curvature_fitting, method)(
                self, self.nn_indices, self.point_basis,
                n_processors=n_processors)
        return self.principle_curvatures, self.principle_directions

    @property
    def gaussian_curvature(self):
        assert hasattr(self, 'principle_curvatures'),\
            'principle curvatures not calculated run \
                compute_principle_curvature_method'
        return self.principle_curvatures[0] * self.principle_curvatures[1]

    @property
    def mean_curvature(self):
        assert hasattr(self, 'principle_curvatures'),\
            'principle curvatures not calculated run \
                compute_principle_curvature_method'
        return (self.principle_curvatures[0] + self.principle_curvatures[1])/2

    @property
    def maximum_curvature(self):
        return self.principle_curvatures[0]

    @property
    def minimum_curvature(self):
        return self.principle_curvatures[1]

    def compute_point_normals(self, points: np.ndarray) -> np.ndarray:
        if not hasattr(self, 'nearest_neighbours'):
            nearest_neighbours = self.compute_nearest_neighbours()
        else:
            nearest_neighbours = self.nearest_neighbours
        centered_nn = nearest_neighbours - points.T[:, :, None]
        covar = np.einsum(
            "ijk, ikl -> ijl ", centered_nn, centered_nn.swapaxes(1, 2)
        )
        if show_tqdm:
            print("calculating the normals from SVD")
        U, s, Vt = np.linalg.svd(covar)
        align_bfs = AlignNormalsBFS(
            self.nn_indices, properties=U, show_progress=show_tqdm
        )
        align_bfs(start_vertex=0)
        return align_bfs.properties

    @PrintMethod("pointing normals outside closed surface'")
    def _align_normals(self) -> None:
        normals = self.point_basis[:, :, -1].T
        centered_points = self - math.mean(self)
        sum_pos = np.sum(math.l2_norm(centered_points + normals))
        sum_neg = np.sum(math.l2_norm(centered_points - normals))
        if sum_neg > sum_pos:
            self.point_basis *= -1
        if not self.external:
            self.point_basis *= -1

    def plot_curvature(self, interval=1, *args, **kwargs):
        f, ax = _CurvatureMultiScatter(
            self, self.principle_curvatures,
            *args, **kwargs
        )(interval=interval)
        return f, ax

    def plot_analytical_curvature(self, interval=1, *args, **kwargs):
        assert hasattr(self, 'analytical')
        f, ax = _CurvatureMultiScatter(
            self, (self.analytical.k_1, self.analytical.k_2),
            *args, **kwargs
        )(interval=interval)

        return f, ax

    def plot_error(self, interval=1, *args, **kwargs):
        assert hasattr(self, 'analytical')
        error_1 = math.metrics.relative_percentage_difference(
            self.analytical.k_1, self.principle_curvatures[0]
        )
        error_2 = math.metrics.relative_percentage_difference(
            self.analytical.k_2, self.principle_curvatures[1]
        )
        f, ax = _CurvatureMultiScatterError(
            self, (error_1, error_2),
            *args, **kwargs
        )(interval=interval)

        return f, ax

    def plot_surface(self, *args, **kwargs):
        if len(args) == 0:
            args = ('.', )
        pyplot.plot3d(*self, *args, **kwargs)

    def check_normals_n_at_a_time(self, interval=1000, n_normals=3) -> None:
        scale = np.mean(self.nn_weights[:, 3])

        for i, (point, normal) in enumerate(
                zip(self.T, self.point_normals.T)):
            if i % interval == 0:
                normal = normal*scale
                I_nearest = self.nn_indices[i]
                # nn = self[:, I_nearest]
                # nn_normals = self.point_normals[I_nearest]
                pyplot.plot3d(*self, '.', alpha=1, markersize=1)
                pyplot.quiver3d(*point, *normal)
                pyplot.equal_aspect_3d_centered(point)
                pyplot.show()

    def check_all_normals(self, interval=100) -> None:
        centroid = math.mean(self)
        scale = np.mean(self.nn_weights[:, 3])
        normals = self.point_normals[:, ::interval]*scale
        pyplot.plot3d(*self[:, ::interval], '.', alpha=1, markersize=1)
        pyplot.quiver3d(
            *self[:, ::interval],
            *normals)
        pyplot.equal_aspect_3d_centered(centroid)
        pyplot.show()

    def write_structured_vtk(self, newshape):
        newshape = list(newshape)

        assert all(
            [
                len(newshape) == 3,
                any(
                    [newshape[0] == 3, newshape[0] == 2]
                )
            ]
        )

        to_write = np.array(self.copy()).reshape(newshape)

        mesh = pv.StructuredGrid(*to_write)

        if hasattr(self, 'principle_curvatures'):
            for name in ('gaussian_curvature', 'mean_curvature', 'maximum_curvature', 'minimum_curvature'):
                temp = np.array(getattr(self, name)).reshape(newshape[1:])
                mesh.points_arrays[name] = temp.squeeze().flatten('F')

    def write_xyz(self, fname='out', encoding='bytes', includeNormals=False, **kwargs):
        if not includeNormals:
            np.savetxt(
                "%s.xyz"%filename, self.T, **kwargs
            )
        else:
            NotADirectoryError

    def to_vtk(
            self, method='pyvista',
            includeNormals=False, includeCurvature=False,
            structuredShape=None, **kwargs):
        """to_vtk

        converts our points surface into a vtk object

        Args:
            method (str, optional): [description]. Defaults to 'pyvista'.
            includeNormals (bool, optional): [description]. Defaults to False.
            includeCurvature (bool, optional): [description]. Defaults to False.
            structuredShape ([type], optional): [description]. Defaults to None.

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """

        if method == 'pyvista':
            flatten_order = 'F'
            if structuredShape is None:
                output = pv.PolyData(self.T, **kwargs)
            else:
                output = pv.StructuredGrid(*self.reshape(structuredShape, **kwargs))

            if includeNormals:
                if hasattr(self, 'point_normals'):
                    if structuredShape is None:
                        output.vectors = self.point_normals.T
                    else:
                        output.vectors = self.point_normals.reshape(structuredShape).reshape(3, -1, order=flatten_order).T
                else:
                    raise Exception('no point normals detected, run compute_all_normals')

            if includeCurvature:
                assert not structuredShape is None, 'a structured shape must be provided'
                mem_shape = (structuredShape[1], structuredShape[2])
                output.point_arrays['maximum_curvature'] = self.maximum_curvature.reshape(mem_shape).flatten(flatten_order)
                output.point_arrays['minimum_curvature'] = self.minimum_curvature.reshape(mem_shape).flatten(flatten_order)
                output.point_arrays['gaussian_curvature'] = self.gaussian_curvature.reshape(mem_shape).flatten(flatten_order)
                output.point_arrays['mean_curvature'] = self.mean_curvature.reshape(mem_shape).flatten(flatten_order)

            return output



if __name__ == "__main__":
    import pathlib
    data_folder = pathlib.Path(
        r'I:\CNNForCFD\test12\true'
        )

    file = data_folder/'00000.vtk'
    pv_obj = pv.read(file)

    points = pv_obj.points.T
    test_points = points[:, ::20]*1000
    # test_points = points*1000
    psurf = Pointsurface(
        test_points, leafsize=100, neighbours=13, external=True)
    psurf.compute_all_normals()
    psurf.compute_principle_curvatures(n_processors=5)
    psurf
    if False:
        ii = 500
        ids = psurf.nn_indices[ii]
        xx, yy = psurf.principle_directions[ii].T
        X, Y, Z = psurf.point_basis[ii].T
        pyplot.plot3d(*psurf, '.', alpha=0.5, markersize=2)
        pyplot.plot3d(*psurf[:, ii, None], 'go')
        pyplot.plot3d(*psurf[:, ids], 'ro')
        pyplot.quiver3d(*psurf[:, ii, None], *X[:, None], color='blue')
        pyplot.quiver3d(*psurf[:, ii, None], *Y[:, None], color='blue')
        pyplot.quiver3d(*psurf[:, ii, None], *Z[:, None], color='green')
        pyplot.quiver3d(*psurf[:, ii, None], *xx[:, None], color='red')
        pyplot.quiver3d(*psurf[:, ii, None], *yy[:, None], color='red')
        pyplot.equal_aspect_3d_centered(psurf[:, ii, None])
        pyplot.show()
    # psurf.plot_curvature()
    # pyplot.show()
    # psurf.check_all_normals(interval=1)
    print('done')
