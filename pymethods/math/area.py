import numpy as np
from ..math import close_curve, make_3d
from ..utils import SequentialFunction

_close_then_make_3d = SequentialFunction(
    close_curve, make_3d
)


def _base_loop(array):
    area = 0
    crossed = np.cross(array[:, 0:-1], array[:, 1:], axis=0)
    area = 0.5*np.sum(np.linalg.norm(crossed, axis=0))
    area = np.abs(area)
    return area


def area(contour: np.array) -> np.float:
    """area

    calculate area of closed 2d contour

    Args:
        contour (np.array): M points x N dimensions

    Returns:
        np.float: area
    """
    contour = _close_then_make_3d(contour)
    area = _base_loop(contour - contour.mean(-1, keepdims=True))
    return area.squeeze()
