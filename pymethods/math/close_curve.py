import numpy as np

def is_closed_curve(contour):
    if not np.allclose(contour[:, 0], contour[:, -1]):
        return False
    return True

def close_curve(contour: np.array, write_end=False) -> np.array:
    """close_curve

    Assume input is a closed contour. Check the 0 and -1 indices.
    If they are not the same append 0 to the array

    Args:
        contour (np.array): N dimension contour x M vectors

    Returns:
        np.array: N dimension contour x M vectors or M + 1 vectors
    """

    if not np.allclose(contour[:, 0], contour[:, -1]):
        if write_end:
            contour[:, -1] = contour[:, 0]
        else:
            contour = np.append(
                contour, contour[:, 0, None], axis=-1)

    return contour
