from ..math import scalar_project, normalize
import numpy as np


def vector_project(
        vector_a: np.array, vector_b: np.array) -> np.array:
    """vector_project

    project vector_a onto vector_b

    https://math.oregonstate.edu/home/programs/undergrad/CalculusQuestStudyGuides/vcalc/dotprod/dotprod.html

    Args:
        vector_a (np.array): M vectors x N dimensions or N dimensions array
        vector_b (np.array): M vectors x N dimensions or N dimensions array

    Returns:
        np.array: M vectors x N dimensions or N dimensions array
    """
    A_scalar_proj_B = scalar_project(vector_a, vector_b)
    return A_scalar_proj_B * normalize(vector_b)
