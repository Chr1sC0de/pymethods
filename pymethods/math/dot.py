import numpy as np
from .. import utils


def dot(vector_a: np.array, vector_b: np.array) -> np.float:
    """dot

    Args:
        vector_a (np.ndarray):
        vector_b (np.ndarray):

    Returns:
        np.ndarray:
    """
    if utils.len_shape(vector_a) == 1:
        vector_a = vector_a[:, None]
    if utils.len_shape(vector_a) == 1:
        vector_b = vector_b[:, None]
    a_dot_b = vector_a.T @ vector_b
    return a_dot_b.squeeze()
