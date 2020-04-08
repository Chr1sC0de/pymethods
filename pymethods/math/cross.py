import numpy as np
from .. import utils


def cross(vectors_a: np.array, vectors_b: np.array) -> np.array:
    """cross

    cross product, if single vector it is faster to
    hard code the cross product rather than use the np.cross method.
    Thus, if a single vector is passed through the hardcoded method is applied.

    Args:
        vectors_a (np.array):
        vectors_b (np.array):

    Returns:
        np.array: crossed vectors
    """
    if utils.is_1d(vectors_a):
        a = vectors_a.squeeze()
        b = vectors_b.squeeze()
        if len(vectors_a) == 3:
            # hardcode the cross product, to maximize speed
            # this option should only be used for sing vectors
            return np.array(
                [
                    a[1]*b[2] - a[2]*b[1],
                    a[2]*b[0] - a[0]*b[2],
                    a[0]*b[1] - a[1]*b[0]
                ]
            )
        else:
            return np.cross(vectors_a, vectors_b, axis=0)
    else:
        return np.cross(vectors_a, vectors_b, axis=0)
