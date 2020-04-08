from typing import Tuple
import numpy as np


def frennet_serret(centreline: np.array) -> np.array:
    """frennet_serret [summary]

    calculate the frennet serret frames
    https://en.wikipedia.org/wiki/Frenet%E2%80%93Serret_formulas

    Args:
        centreline (np.array): M vectors x N dimensions

    Returns:
        np.array:  Normal, Binormal, Tangent of curve
                3 x N dimensions x N dimensions
    """
    dX = centreline.grad
    dXX = dX.grad
    T = dX.normalize()
    # calculate the normal
    U = dX.cross(dXX).normalize()
    V = U.cross(T).normalize()
    U = V.cross(T).normalize()
    return np.stack([U, V, T], axis=0)
