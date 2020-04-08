from ..math import normalize, vector_project
import numpy as np


def project_to_plane(
        vectors: np.array, normal: np.array) -> np.array:
    """project_to_plane

    project the vectors to plane described by vector, this is unscaled

    Args:
        vectors (np.array): M vectors x N dimensions
        normal (np.array): 1 x N dimensions or N dimensions

    Returns:
        np.array: M vectors x N dimensions
    """
    vectors = vectors.squeeze()
    normal = normal.squeeze()
    normal = normalize(normal)
    parallel = vector_project(vectors, normal)
    return vectors - parallel
