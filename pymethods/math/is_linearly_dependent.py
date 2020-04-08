import numpy as np
from typing import (
    Tuple
)


def is_linearly_dependent(*args: Tuple[np.array]) -> bool:
    """is_linearly_dependent

    takes in either a single np.array of vectors or
    *args of vectors and checks whether they
    are linearly dependent

    Returns:
        bool:
    """
    if len(args) == 1:
        array = np.array(args[0])
    else:
        array = np.stack(
            args, axis=-1
        )
    if np.isclose(np.linalg.det(array), 0):
        return False
    return True


def make_linearly_independent(vectors: np.ndarray, out=False) -> np.ndarray:
    """make_linearly_independent

    gets the set of linearly independent vector from
    a set of vectors

    Args:
        vectors (np.ndarray): N dimensions x M points

    Returns:
        np.ndarray:
    """
    vector_copy = vectors.copy()
    U, S, Vt = np.linalg.svd(vector_copy)
    vector_copy = Vt.T @ U.T
    # special reflection case
    if np.linalg.det(vector_copy) < 0:
        if out:
            print("Reflection detected")
        vector_copy[2, :] *= -1
    return vector_copy
