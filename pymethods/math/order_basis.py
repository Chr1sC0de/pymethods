from ..math import (
    mean, normalize, scalar_project, mean_square
    )
import numpy as np


def order_basis(vectors: np.array, basis: np.array) -> np.array:
    """order_basis

    we want the basis to be ordered in [[i], [j], [k]]. i and j can be
    arbitrary however k must be consistent and should point normal to the plane

    Args:
        vectors (np.array): M Vectors x N dimension array
        basis (np.array): 3 Vectors x N dimension array

    Returns:
        np.array: 3 Vectors x N dimension array
    """
    # find the k_indice
    n_dims, _ = basis.shape
    assert n_dims == 3, "basis must be 3d"
    centered_input = vectors - mean(vectors)
    x_vector = centered_input[:, 0]
    check_scalar_project_k = np.zeros(n_dims)
    check_scalar_project_i = np.zeros(n_dims)
    possible_inds = np.arange(n_dims)
    for i in list(range(len(basis))):
        scalar_projected_k = scalar_project(centered_input, basis[:, i])
        scalar_projected_i = scalar_project(x_vector, basis[:, i])
        error_k = mean_square(scalar_projected_k)
        error_i = mean_square(scalar_projected_i)
        check_scalar_project_k[i] = error_k
        check_scalar_project_i[i] = error_i
    k_ind = np.argmin(check_scalar_project_k)
    i_ind = np.argmax(check_scalar_project_i)
    assert k_ind != i_ind, "k_ind equals i_ind"
    # now check the remaining dimensions
    for i in possible_inds:
        if i not in [k_ind, i_ind]:
            j_ind = i
    return normalize(basis[:, [i_ind, j_ind, k_ind]])

if __name__ == "__main__":
    pass

