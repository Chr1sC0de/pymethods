import numpy as np
try:
    from pymethods import math
    from pymethods import pyplot as plt
except ImportError:
    from .. import math
    from .. import pyplot as plt


def argSortByBasis(array, ref_basis, n_to_check=20):
    """arg_basis_sort [summary]

    For an ndarray describing the points along a closed contour and a ref_basis
    which describes the plane outpud the ids of the sorted points. The points are sorted such that
    the ndarray[0,:] is the point closest to the i-axis and the orientation of rotation
    is determined by the closest point

    Args:
        ndarray (_np.ndarray)  : N x M matrix where N is the number of points
            and M is the total number of dimensions
        ref_basis (_np.ndarray): 3 x 3 basis matrix discribing
        return_ref (bool, optional): return a copy of ndarray in the
            ref_basis frame. Defaults to True.
    Returns:
        _np.ndarray: list of sorted indices
    """
    meanLocation = np.mean(array, axis=-1, keepdims=True)
    ndarray_centered = array - meanLocation
    n_pts = ndarray_centered.shape[-1]
    # ndarray_centered_2d
    A = ref_basis.T @ ndarray_centered
    ids_vector = np.arange(n_pts)[None, :]
    # concatenate A with id vector
    A_concat = np.concatenate([A, ids_vector], axis=0)
    # initialize a vectore to store the sorted
    sorted_ids = np.zeros(A_concat.shape[-1])
    # reference_basis_2d
    ijk = np.identity(3)
    # project A to the i direction
    project_to_x = math.scalar_project(A, ijk[:, 0, None])
    # ids of points moving in the positive direction
    to_use_ids = np.where(project_to_x > 0)[0]
    # subsample ndarray_centered_2d_concat_with_ids
    subset = A_concat[:, to_use_ids]
    # project the subset values to j
    project_to_y = math.scalar_project(subset[0:-1, :], ijk[1, :])
    # locate the key of the point which is closest to the x axis of the subset
    id_of_subset = np.argmin(np.abs(project_to_y))
    # get the id of the starting point
    start_id = int(subset[-1, id_of_subset])
    # store the starting point in the initialesd vector
    sorted_ids[0] = start_id
    # create a copy of the current point
    current_pt = A_concat[0:-1, start_id, None].copy()
    # delete this point from the ndarray_centered_2d concated with an id vector
    copy_A_cont = np.delete(A_concat, start_id, axis=-1)
    counter = 0
    while copy_A_cont.shape[-1] > 0:
        if copy_A_cont.shape[-1]:
            closest_ind = np.argmin(
                np.linalg.norm(copy_A_cont[0:-1] - current_pt, axis=0))
        counter += 1
        assert counter < n_pts*2, \
            'too many iterations something is wrong with the code'
        current_pt = copy_A_cont[0:-1, closest_ind, None]
        sorted_ids[counter] = int(copy_A_cont[-1, closest_ind])
        copy_A_cont = np.delete(copy_A_cont, closest_ind, axis=-1)

    sorted_ndarray_in_ref = A[:, sorted_ids.astype(int)]
    # check if clockwise
    check = 0
    base_vector = math.normalize(sorted_ndarray_in_ref[:, 0, None])

    for i in list(range(n_to_check)):
        test_vector = math.normalize(sorted_ndarray_in_ref[:, i, None])
        check += math.cross(base_vector, test_vector)[-1]

    # if not rotating clockwise then flip order so that
    # points rotate in a clockwise direction
    if check < 0:
        sorted_ids = np.flipud(sorted_ids)
        sorted_ids = np.roll(sorted_ids, 1)

    return np.array([int(i) for i in sorted_ids])


def sortByBasis(self, returnBasis=False, ref_basis=None):
    """arg_basis_sort

    For an ndarray describing the points along a closed contour and a ref_basis
    which describes the plane, return the sorted points. The points are sorted such that
    ndarray[0,:] is the point closest to the i-axis of ref_basis and the points in increasing order describe a
    rotation in the clockwise direction of the given ref_basis.

    Args:
        ndarray (_np.ndarray)  : N x M matrix where N is the number of points
            and M is the total number of dimensions
        ref_basis (_np.ndarray): 3 x 3 basis matrix discribing
        n_to_check (int, optional): number of points to check for
            clockwise rotation. Number of points should not be beyond the j-axis
            as the orientation will be flipped. Defaults to 20.
    Returns:
        _np.ndarray: list of sorted points
    """
    NotImplemented