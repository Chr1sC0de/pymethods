import numpy as np
from .. import utils


def make_3d(vectors: np.array) -> np.array:
    """make_3d

    For an 2 x N array convert it into 3 x N by concatenating
    a 0 column vector of length end

    Args:
        vectors (np.array): 2 dimensions x M vectors

    Returns:
        np.array: 3 dimensions x M vectors
    """
    if utils.len_shape(vectors) == 1:
        vectors = vectors[:, None]
    dims, pts = vectors.shape
    if dims < 3:
        new_vectors = np.zeros((3, pts))
        new_vectors[0:dims, :] = vectors
        return new_vectors.squeeze()
    else:
        return vectors.squeeze()
