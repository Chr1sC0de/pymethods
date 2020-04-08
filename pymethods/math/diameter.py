from ..math import area, mean
import numpy as np


def area_assumed_diameter(contour: np.array) -> np.float:
    """area_assumed_diameter

    calculate the area assumed diameter

    Args:
        contour (np.array): M vectors x N dimensions

    Returns:
        np.float: diameter
    """
    contour_area = area(contour)
    d = 2*np.sqrt(contour_area / np.pi)
    return d


def all_diameters(contour: np.array) -> np.float:
    """all_diameters

    for a contour in 2d calculate all the diameters

    Args:
        contour (np.array): M vectors x N dimensions

    Returns:
        np.float: diameter
    """
    normal = np.array([[0, 0, 1]])
    centroid = mean(contour)
    centered = contour - centroid
    all_diameters = []
    for pnum, point in enumerate(centered):
        point = point[None, :]
        r_current = np.linalg.norm(point)
        perp = np.cross(point[None, :], normal)[0]
        inner = np.inner(centered, perp)
        potential = []
        NTRIES = 10
        while len(potential) == 0:
            sortedProj = np.argsort(np.abs(inner.squeeze()))[0:NTRIES]
            sortedProj = [i for i in sortedProj if i != pnum]
            testingPoints = centered[sortedProj]
            test_points_inner = np.inner(testingPoints, point)
            potential = test_points_inner[test_points_inner < 0]
            NTRIES += 1
        diameter = r_current + np.abs(potential[0])
        all_diameters.append(diameter)
    return np.array(all_diameters)
