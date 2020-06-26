import numpy as np
from .. import math


def frennet_serret_with_transport(
        centreline: np.array) -> np.array:
    """frennet_serret_with_transport

    calcualate frennet frames
    https://janakiev.com/blog/framing-parametric-curves/

    Args:
        centreline (np.array): N x M points

    Returns:
        np.array: Normal, Binormal, Tangent of curve
                3 x N dimensions x N dimensions
    """
    n = centreline.shape[-1]
    dX = np.gradient(centreline, axis=-1, edge_order=1)
    T = math.normalize(dX)
    V = np.zeros_like(centreline)
    V[:, 0] = math.normalize(
        math.cross(T[:, 0], T[:, 1])
    )
    for i in np.arange(n-1):
        B = math.cross(T[:, i], T[:, i+1])
        if math.l2_norm(B) < 0.0001:
            V[:, i+1] = V[:, i]
        else:
            B = math.normalize(B).squeeze()
            dot_ti_tip1 = math.dot(T[:, i], T[:, i+1])
            phi = np.arccos(dot_ti_tip1).squeeze()
            R = math.rotation_matrix(B, phi)
            V[:, i+1] = R @ V[:, i]
    U = math.normalize(math.cross(V, T))
    V = math.normalize(math.cross(T, U))
    return np.stack([U.T, V.T, T.T], axis=-1)
