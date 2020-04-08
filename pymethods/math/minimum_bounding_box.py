import numpy as np


def minimum_bounding_box(array: np.ndarray) -> np.ndarray:
    """minimum_bounding_box

    Calculate the minumim bounding box for an array of points

    Args:
        array (np.ndarray): N dimensions x M points

    Returns:
        np.ndarray: N dimensions x 2 points
    """
    array = np.asarray(array)
    n_dims, _ = array.shape
    bounds = np.zeros((n_dims, 2))
    dim_mins = np.argmin(array, axis=-1)
    dim_maxs = np.argmax(array, axis=-1)
    ind_min_max = np.stack(
        [dim_mins, dim_maxs], axis=-1
    )
    for i, min_max in enumerate(ind_min_max):
        bounds[i, :] = array[i, min_max]
    return bounds
