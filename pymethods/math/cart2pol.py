import numpy as np


def cart2pol(vectors: np.array, returnRad=False) -> np.array:

    """cart2pol

    convert N x 2 nd array from cartesian to polar

    Args:
        vectors (np.array): 2 dimensions x M vectors

    Returns:
        np.array: 2 dimensions x M vectors
    """

    x = vectors[0, :]
    y = vectors[1, :]
    r = np.sqrt(x**2+y**2)
    theta = np.arctan2(y, x)

    return np.stack([theta, r], axis=0)
