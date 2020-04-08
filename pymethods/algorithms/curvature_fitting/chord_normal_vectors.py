import numpy as np
import scipy.optimize as sco
import typing
from tqdm import tqdm
from scipy.linalg import eig
from ...multiprocess import NumpyMulti
from pymethods import pyplot as plt


_debug_ = False 


def _W_solve(k1, k2, theta):
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    A = k1*cos_theta ** 2 + k2*sin_theta**2
    B = (k2-k1)*cos_theta*sin_theta
    C = k1*sin_theta ** 2 + k2*cos_theta**2
    return np.array(
        [
            [A, B],
            [B, C]
        ]
    )


def _funky2(k1_k2_theta, M, R):
    k1, k2, theta = k1_k2_theta
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    A = k1 * cos_theta ** 2 + k2 * sin_theta ** 2
    B = (k2 - k1) * cos_theta * sin_theta
    C = k1 * sin_theta ** 2 + k2 * cos_theta ** 2
    mu = np.array([A, B, C]).T
    return np.abs(M @ mu - R)


def _debug(nn_in_L, nn_normals_in_l):
    origin = [0, 0, 0]
    i = 500
    j = 2
    plt.plot3d(
        *nn_in_L[i], '.'
    )
    plt.quiver3d(
        *nn_in_L[i][:, j], *nn_normals_in_l[i][:, j]
    )
    plt.equal_aspect_3d_centered(origin)
    plt.show()


def can_lsq_fit(
        main_array: np.ndarray, adj_list: np.ndarray,
        point_basis: np.ndarray,
        n_processors=None, eps=1e7) -> typing.Iterable[np.ndarray]:
    """can_lsq_fit

        A python implementation of Curvature Estimation of 3D Point Cloud Surfaces
        Through the Fitting of NormalSection Curvatures
        http://www.nlpr.ia.ac.cn/2008papers/gjhy/gh129.pdf

        Args:
            main_array (np.ndarray): pointcloud array 3xN
            adj_list (np.ndarray): adjacency list NxKNN
            point_basis (np.ndarray): Nx3x3

        Returns:
            typing.Iterable[np.ndarray]: principle_curvatures, principle_directions
    """
    # initialize the principle curvatures and directions
    # the nn_points the nn normals and the XY points
    principle_curvatures = np.zeros((2, main_array.shape[-1]))
    principle_directions = np.zeros(
        (main_array.shape[-1], main_array.shape[0], 2))
    nn_points_all = np.zeros(
        (main_array.shape[1], main_array.shape[0], adj_list.shape[-1]))
    nn_normals_all = np.zeros(
        (main_array.shape[1], main_array.shape[0], adj_list.shape[-1]))
    point_normals = point_basis[:, :, -1].T
    XY = point_basis[:, :, 0:2]
    for i, ids in enumerate(adj_list):
        nn_points_all[i] = main_array[:, ids].copy()
        nn_normals_all[i] = point_normals[:, ids].copy()
    centered_nn = nn_points_all - main_array.T[:, :, None]
    # locate points that will blow up
    i_row, i_col = np.where(
        np.isclose(np.linalg.norm(centered_nn, axis=1), 0))
    centered_nn[i_row, :, i_col] = np.nan
    # change the co-ordinate system of the centered nearest
    nn_in_L = np.einsum(
        'nij,njk->nik', point_basis.swapaxes(1, 2), centered_nn
    )
    nn_normals_in_l = np.einsum(
        'nij,njk->nik', point_basis.swapaxes(1, 2), nn_normals_all
    )
    # get the dot product
    n_xy_num = np.einsum(
        'ijk,ijk->ik', nn_in_L[:, 0:2, :], nn_normals_in_l[:, 0:2, :]
    )
    n_xy_denom = np.linalg.norm(
        nn_in_L[:, 0:2, :], axis=1,
    )
    n_xy = n_xy_num/n_xy_denom
    n_z = nn_normals_in_l[:, -1, :]
    k_i_n_denom_A = np.sqrt(n_xy ** 2 + n_z ** 2)
    k_i_n_denom_B = n_xy_denom
    k_i_n_denom = k_i_n_denom_A * k_i_n_denom_B
    k_i_n = -n_xy/k_i_n_denom
    Q_i = nn_in_L[:, 0:2, :]
    Q_i_hat = Q_i/np.linalg.norm(Q_i, axis=1)[:, None, :]
    theta = np.arctan2(Q_i_hat[:, 1, :], Q_i_hat[:, 0, :])
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    R = k_i_n
    M = np.stack(
        [
            cos_theta**2,
            2*cos_theta*sin_theta,
            sin_theta**2
        ], axis=-1
    )
    k_i_n[k_i_n > eps] = np.nan
    k_i_n[k_i_n < -eps] = np.nan

    if _debug_:
        _debug(nn_in_L, nn_normals_in_l)

    if any([n_processors is None, n_processors == 1]):

        for i, (kk, m, r, t, xy) in tqdm(
                enumerate(zip(k_i_n, M, R, theta, XY)), total=len(M),
                disable=(not _debug_)):
            III = np.argwhere(
                np.isfinite(kk)
                ).squeeze()
            kk = kk[III]
            m = m[III]
            r = r[III]
            t = t[III]
            mu = sco.lsq_linear(
                m, r, tol=1e-12
            )
            A, B, C = mu.x
            W = np.array(
                [
                    [A, B],
                    [B, C]
                ]
            )
            eigs, v = eig(W, overwrite_a=True, check_finite=False)
            vglob = np.real(xy @ v)
            eigs = np.real(eigs)
            sorted_indices = np.flipud(np.argsort(eigs))
            eigs = eigs[sorted_indices]
            vglob = vglob[:, sorted_indices]
            principle_curvatures[:, i] = eigs
            principle_directions[i, :] = vglob
    else:
        mp_solver = CAN_LSQ_FIT(
            k_i_n, M, R, theta, XY,
            principle_curvatures=principle_curvatures,
            principle_directions=principle_directions,
            n_processors=n_processors)
        mp_solver.run()
        principle_curvatures = mp_solver.principle_curvatures
        principle_directions = mp_solver.principle_directions
    return principle_curvatures, principle_directions


class CAN_LSQ_FIT(NumpyMulti):

    def __init__(self, k_i_n, M, R, theta, XY, *args,
                 principle_curvatures, principle_directions, **kwargs):
        arg_dict = dict(
            k_i_n=k_i_n, M=M, R=R, theta=theta, XY=XY
        )
        # make the data shared
        self.principle_curvatures = principle_curvatures
        self.principle_directions = principle_directions
        self.n_total = self.principle_directions.shape[-1]
        super(CAN_LSQ_FIT, self).__init__(
            arg_dict, **kwargs
        )

    def reconstruct_arrays(self):
        idx, (eigs, vglob) = self.mp_queue.get()
        self.principle_curvatures[:, idx] = eigs
        self.principle_directions[idx, :] = vglob

    def decompose_arrays(self):
        zipped_dict = super(CAN_LSQ_FIT, self).decompose_arrays()
        zipped_dict = list(zipped_dict)
        accumulator = 0
        for i, _ in zipped_dict:
            zipped_dict[i] = list(zipped_dict[i])
            zipped_dict[i][0] = accumulator
            accumulator += zipped_dict[i][1][0].shape[0]
        return zipped_dict

    @staticmethod
    def worker(mp_q, idx, *args):
        import numpy as np
        import scipy.optimize as sco

        k_i_n, M, R, theta, XY = args
        for i, (kk, m, r, t, xy) in tqdm(
                enumerate(zip(k_i_n, M, R, theta, XY)), total=len(M),
                disable=(not _debug_)):
            III = np.argwhere(
                np.isfinite(kk)
                ).squeeze()
            kk = kk[III]
            m = m[III]
            r = r[III]
            t = t[III]
            mu = sco.lsq_linear(
                m, r, tol=1e-12
            )
            A, B, C = mu.x
            W = np.array(
                [
                    [A, B],
                    [B, C]
                ]
            )
            eigs, v = eig(W, overwrite_a=True, check_finite=False)
            vglob = np.real(xy @ v)
            eigs = np.real(eigs)
            sorted_indices = np.flipud(np.argsort(eigs))
            eigs = eigs[sorted_indices]
            vglob = vglob[:, sorted_indices]
            mp_q.put(
                (
                    idx + i, (eigs, vglob)
                )
            )


if __name__ == "__main__":
    pass
