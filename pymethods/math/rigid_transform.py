from ..math import least_squares_fitting_of_two_point_sets
import numpy as np


def rigid_transform(
        vector_a: np.array, vector_b: np.array) -> np.array:
    """rigid_transform

    rigidly transform vector_a onto vector_b

    Args:
        vector_a (np.ndarray): staring location of
           N dimensions x M vectors
        vector_b (np.ndarray): vectors to transform vector_a to
            must be same shape as vector_a, N dimensions x M vectors

    Returns:
        List[np.ndarray]: vector_a rigidly transformed onto vector_b
            M vectors x N dimensions
    """

    R, t = least_squares_fitting_of_two_point_sets(vector_a, vector_b)
    rigid_transformed = R @ vector_a + t
    return rigid_transformed

