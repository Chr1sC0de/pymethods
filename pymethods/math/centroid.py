from ..math import (
    mean, area
)
import numpy as np
from ..math import close_curve, make_3d

def contour_centroid_legacy(contour: np.array, basis: np.array) -> np.array:
    """get_centroid_of_cross_section

    get centroid of a closed contour using 2d greene's theorem
    by projectiing it onto the basis in 2d

    https://leancrew.com/all-this/2018/01/greens-theorem-and-section-properties/

    Args:
        contour ([nd.array]): N x M points
        basis ([nd.array]): 3 x 3 matrix of where the contour lies

    Returns:
        np.array: 1 x 3 location of centroid
    """
    contour_copy = contour.copy()
    mean_location = mean(contour_copy)
    contour_copy = contour_copy - mean_location
    contour_copy = basis @ contour_copy
    contour_copy = close_curve(contour_copy)
    sx = sy = 0
    a = area(contour_copy)
    x = contour_copy[:, 0]
    y = contour_copy[:, 1]
    for i in range(len(contour_copy) - 1):
        sx += (x[i] + x[i+1])*(x[i]*y[i+1] - x[i+1]*y[i])
        sy += (y[i] + y[i+1])*(x[i]*y[i+1] - x[i+1]*y[i])
    centroid = np.array([[sx/(6*a), sy/(6*a), 0]])
    centroid = basis.T @ centroid + mean_location
    return centroid


def contour_centroid(contour: np.array, axis=0) -> np.array:
    """get_centroid_of_cross_section

    get centroid of a closed contour using 2d greene's theorem
    by projectiing it onto the basis in 2d

    https://leancrew.com/all-this/2018/01/greens-theorem-and-section-properties/

    Args:
        contour ([nd.array]): N x M points
        basis ([nd.array]): 3 x 3 matrix of where the contour lies

    Returns:
        np.array: 1 x 3 location of centroid
    """
    contour = close_curve(make_3d(contour))
    mean_location = mean(contour)
    contour = contour - mean_location
    contour_area = area(contour)
    area_elements = np.cross(
        contour[:, 0:-1], contour[:, 1:], axis=axis
    )
    integral_elements = contour[:, 0:-1] * area_elements
    centroid = np.sum(integral_elements, axis=-1)/contour_area + mean_location.squeeze()
    return centroid


