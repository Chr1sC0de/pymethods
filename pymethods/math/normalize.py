from ..math import l2_norm
import numpy as np


def normalize(vector_a: np.array) -> np.array:
    """normalize

    Args:
        vector_a (np.array): N dimension array x M Vectors

    Returns:
        np.array: N dimension array x M Vectors
    """
    return vector_a/l2_norm(vector_a, keepdims=True)
