import numpy as np
from typing import Tuple
import logging

def least_squares_fitting_of_two_point_sets(
        vector_a: np.array, vector_b: np.array) -> Tuple[np.array]:
    """least_squares_fitting_of_two_point_sets

    estimate rigd transform required to move vector_a
    such that it overlaps vector_b

    http://nghiaho.com/?page_id=671

    Args:
        vector_a (np.array): N dimensions x M points
        vector_b (np.array): N dimensions x M points

    Returns:
        Tuple[np.array]: [rotation, translation] matrices

    """
    centroid_a = np.mean(vector_a, axis=-1)
    centroid_b = np.mean(vector_b, axis=-1)
    # centre the points
    AA = vector_a - centroid_a[:, None]
    BB = vector_b - centroid_b[:, None]
    # dot is matrix multiplication for array
    H = AA @ BB.T
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    # special reflection case
    if np.linalg.det(R) < 0:
        logging.debug("reflection detected")
        R[2, :] *= -1
    t = -(R @ centroid_a) + centroid_b
    return R, t[:, None]
