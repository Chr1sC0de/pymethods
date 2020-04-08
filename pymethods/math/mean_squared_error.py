import numpy as np
from .. import math


def mean_square_error(array_a: np.array, array_b: np.array) -> np.array:
    """mean_square_error

    https://en.wikipedia.org/wiki/Mean_squared_error

    Args:
        array_a (np.array):
        array_b (np.array):
    """
    error = array_a - array_b
    return math.mean_square(error)