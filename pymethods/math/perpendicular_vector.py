from .. import math
import numpy as np


def vector_perpendicular(
        vectors_a: np.ndarray, vectors_b: np.ndarray) -> np.ndarray:
    """perpendiculr_vectors

    calculate the component of vector_a perpendicular to vector_b

    Args:
        vectors_a (np.ndarray): [description]
        vectors_b (np.ndarray): [description]

    Returns:
        np.ndarray: [description]
    """
    vectors_a = vectors_a.squeeze()
    vectors_b = vectors_b.squeeze()
    a_vector_proj_b = math.vector_project(vectors_a, vectors_b)
    return vectors_a - a_vector_proj_b
