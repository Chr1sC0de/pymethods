import numpy as np
from pymethods import math
from pymethods.utils import len_shape


def scalar_project(
        vector_a: np.array,
        vector_b: np.array, *kwargs: dict) -> np.array:

    """scalar_project

    https://math.oregonstate.edu/home/programs/undergrad/CalculusQuestStudyGuides/vcalc/dotprod/dotprod.html

    Args:
        vector_a (np.array): N dimensions x M vectors
        vector_b (np.array): N dimensions x M, 1, 3 vectors

    Returns:
        np.array: M vectors x N dimensions or N dimensions array

    """
    vector_b_hat = math.normalize(vector_b)
    return math.dot(vector_a, vector_b_hat).T