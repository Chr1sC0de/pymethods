import numpy as np
from .. import utils


def len_shape(obj: object) -> int:
    """len_shape

    len the length of the shape of an object

    Args:
        obj (object): object with shape
            property

    Returns:
        int: the length of the shape
    """

    return len(obj.shape)


def is_1d(vectors: np.array) -> bool:
    """is_1d

    check if the object is 1 dimensional

    Args:
        vectors (np.array): array to check

    Returns:
        bool: True if the data is 1d False if not
    """

    if len_shape(vectors) == 1:
        return True
    elif len_shape(vectors) == 2:
        if utils.len_dim_shape_shortest(vectors) == 1:
            return True
    else:
        return False


def make_column(vectors: np.ndarray) -> np.ndarray:
    """make_column

    convert a vector into column vector. This assumes that the vector
    has lenshape 1 otherwise it is passed directly

    Args:
        vectors (np.ndarray):

    Returns:
        np.ndarray:
    """

    if is_1d(vectors):
        if utils.len_shape(vectors) == 1:
            return vectors[:, None]
    return vectors


def make_row(vectors: np.ndarray) -> np.ndarray:
    """make_row

    convert a vector into row vector. This assumes that the vector
    has lenshape 1 otherwise it is passed directly

    Args:
        vectors (np.ndarray):

    Returns:
        np.ndarray:
    """

    if is_1d(vectors):
        if utils.len_shape(vectors) == 1:
            return vectors[None, :]
    return vectors
