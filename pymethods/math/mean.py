import numpy as np
from typing import Union


def mean(vector_a: np.array) -> Union[np.float, np.array]:
    """mean

    Args:
        vector_a (np.array): N dimension or M Vector x N dimension
            array

    Returns:
        Union[np.float, np.array]: mean of input vector/vectors
    """
    return np.mean(vector_a, axis=-1, keepdims=True)
