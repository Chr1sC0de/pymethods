from ..math import order_basis, normalize
import numpy as np


def approximate_basis(vectors: np.array) -> np.array:
    """approximate_basis

    approximate the basis for the input vectors

    Args:
        vectors (np.array): M Vectors x N Dimensions

    Returns:
        np.array: N Dimensions x N Dimensions
    """
    n_elems = len(vectors.T)
    cov = (vectors @ vectors.T)/n_elems
    U, _, _ = np.linalg.svd(cov)
    return normalize(U)


def approximate_normal(vectors: np.array) -> np.array:
    """approximate_normal

    approximate the normal for the input vectors

    Args:
        vectors (np.array): M Vectors x N Dimensions

    Returns:
        np.array: N Dimensions
    """
    return approximate_basis(vectors)[:, -1]