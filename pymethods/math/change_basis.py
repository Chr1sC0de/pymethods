import numpy as np


def change_basis(x: np.array, basis: np.array) -> np.array:
    """change_basis

    https://en.wikiversity.org/wiki/Tensors/Transformation_rule_under_a_change_of_basis]
    Best Vid on change of reference frames
    https://www.youtube.com/watch?v=P2LTAUO1TdA

    Args:
        x (np.array): M vectors x N dimensions
        basis (np.array): N dimensions x N dimensions

    Returns:
        np.array: M vectors x N dimensions
    """
    return R @ x
