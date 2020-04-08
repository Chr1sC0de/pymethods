import numpy as np
from typing import Union
from .. import utils
from .. import math as _math
import math
_methods = ['linalg', 'einsum', '3d', '1d']


def l2_norm(vector_a: np.array, keepdims=True) -> Union[np.float, np.array]:
    """l2_norm

    calculates the l2_norm commonly associated
    with the magnitude of a vector.

    Args:
        vector_a (np.array): N dimension or M Vector x N dimension
            array
        method (str): string specifying which method to use

    Returns:
        Union[np.float, np.array]: l2_norm of input vector/vectors
    """
    return np.linalg.norm(vector_a, axis=0, keepdims=keepdims)
