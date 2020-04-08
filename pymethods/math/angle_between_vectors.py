import numpy as np
from .. import math
from .. import utils

lenshape = utils.len_shape


def smallest_angle_between_vectors(
        vectors_a: np.ndarray, vectors_b: np.ndarray,
        direction=None) -> np.ndarray:
    """angle_between_vectors

    calculate the angle between two vectors in radians

    Args:
        vectors_a (np.ndarray): N dimensions x M Vectors
        vectors_b (np.ndarray): N dimensions x M or 1 Vectors
        basis (np.ndarray): basis indicating how the
            angle should be calculated

    Returns:
        np.ndarray: array containing the angles of the vectors
    """
    mag_a = math.l2_norm(vectors_a)
    mag_b = math.l2_norm(vectors_b)
    a_dot_b = math.dot(vectors_a, vectors_b)
    return np.arccos(a_dot_b/(mag_a * mag_b)).squeeze()


def directed_angle(
        vector_a: np.ndarray, vector_b: np.ndarray,
        direction: np.ndarray) -> np.ndarray:
    """directed_angle

    calculate the angle however use information from
    a direction, for example the normal, to determine the correct angle.
    The angle is calculated counter clockwise from the direction.

    Args:
        vector_a (np.ndarray):
        vector_b (np.ndarray):
        direction (np.ndarray): normal direction

    Returns:
        np.ndarray: array of angles
    """
    if not _check_correct_shape(vector_a, vector_b):
        raise ValueError(
            f"cannot get directed angle\
                 from vectors of shape {vector_a.shape} and {vector_b.shape}")
    direction = utils.make_column(np.array(direction))
    angles = smallest_angle_between_vectors(vector_a, vector_b)
    vector_a = utils.make_column(vector_a)
    vector_b = utils.make_column(vector_b)
    if vector_a.shape[-1] == vector_b.shape[-1]:
        for i, (a, b) in enumerate(zip(vector_a.T, vector_b.T)):
            quadrant = _directed_angle_body(a, b, direction)
            angles[i] = _control_angle(quadrant, angles[i])
    else:
        # we are assuming that the vector_a is a single column vector
        a = vector_a.squeeze()
        for i, b in enumerate(vector_b.T):
            quadrant = _directed_angle_body(a, b, direction)
            controlled_angle = _control_angle(quadrant, angles[i])
            angles[i] = controlled_angle
    return angles


def _directed_angle_body(a, b, direction):
    perp = math.vector_perpendicular(direction, a)
    k = math.normalize(perp)
    i = math.normalize(a)
    j = math.normalize(math.cross(k, i))
    ijk = np.stack([i, j, k], axis=0)
    x, y, _ = math.scalar_project(b, ijk)
    return _get_quadrant(x, y)


def _check_correct_shape(vector_a, vector_b):
    check_1 = lenshape(vector_a) == 2
    check_2 = lenshape(vector_b) == 2
    if all([check_1, check_2]):
        if vector_a.shape[-1] == vector_b.shape[-1]:
            return True
        check_3 = vector_a.shape[-1] != vector_b.shape[-1]
        check_4 = vector_a.shape[-1] == 1
        if all([check_3, check_4]):
            return True
    else:
        if lenshape(vector_a) == 1:
            return True
        if vector_a.shape[-1] == vector_b.shape[-1]:
            return True
    return False


def _control_angle(quandrant, minor_angle):
    if quandrant == 0:
        return minor_angle
    if quandrant == 1:
        return minor_angle
    if quandrant == 2:
        return 2 * np.pi - minor_angle
    if quandrant == 3:
        return 2 * np.pi - minor_angle


def _get_quadrant(x, y):
    if all([x >= 0, y >= 0]):
        return 0
    if all([x <= 0, y >= 0]):
        return 1
    if all([x <= 0, y <= 0]):
        return 2
    if all([x >= 0, y <= 0]):
        return 3
