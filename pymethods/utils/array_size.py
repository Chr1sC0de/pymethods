import numpy as np
from sys import getsizeof

def memory_size(array: np.ndarray, out='bytes'):
    array = np.array(array)
    return getsizeof(array)