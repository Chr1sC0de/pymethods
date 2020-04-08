import numpy as np


def pol2cart(vectors: np.array) -> np.array:
    """pol2cart

    convert N x 2 ndarray from polar to cartesian

    Args:
        vectors (np.array): M vectors x 2 dimensions

    Returns:
        np.array: M vectors x 2 dimensions
    """
    theta = vectors[:, 0]
    r = vectors[:, 1]
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return np.stack([x, y], axis=-1)
