import numpy as np


def skew_symmetric_3d(vector: np.array) -> np.array:
    """skew_symmetric_3d

    https://en.wikipedia.org/wiki/Skew-symmetric_matrix

    Args:
        vector (np.array): 1 x N dimension or N Dimension

    Returns:
        np.array: N dimension x N dimension array
    """
    vector = vector.squeeze()
    skew_sym = np.array([[0.0, -vector[2], vector[1]],
                        [vector[2], 0.0, -vector[0]],
                        [-vector[1], vector[0], 0]])
    return skew_sym
