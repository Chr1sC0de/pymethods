import numpy as np
from .. import math


def rotation_matrix(vector: np.array, angle: np.float) -> np.array:
    """rotation_matrix

    calculate rotation matrix required to rotate points about vector by
    phi https://en.wikipedia.org/wiki/Rotation_matrix

    Args:
        vector (np.array): 3 dimension axis of rotation
        angle (np.float): radians, angle to rotate around vector right hand
            rule

    Returns:
        np.array: 3 x 3 rotation matrix
    """
    dims, = vector.shape
    axis = math.normalize(vector)
    outer = np.outer(axis, axis)
    R = np.cos(angle) * np.identity(dims) \
        + np.sin(angle) * math.skew_symmetric_3d(axis) \
        + (1-np.cos(angle)) * outer
    return np.array(R)
