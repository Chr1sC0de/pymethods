import numpy as np
from typing import Union
from .. import utils
from typing import Iterable
from functools import partial

_is_shortest = utils.IsSubsetString('shortest')
_is_longest = utils.IsSubsetString('longest')
_in_aliases = utils.Isin(
    _is_shortest.decomposed_string,
    _is_longest.decomposed_string)
_is_string = utils.Isinstance(str)


def len_dim_shape_shortest(obj: object) -> int:
    """len_dim_shape_shortest

    Find the len of the shortest dimension of array
    or object with shape property that contains a __len__ method

    Args:
        array (object): object containing a shape
            property with a len method

    Returns:
        int: len of shape
    """
    obj_shape = obj.shape
    min_obj_shape = np.argmin(obj_shape)
    return obj.shape[min_obj_shape]


def len_dim_shape_longest(obj: object) -> int:
    """len_dim_shape_longest [summary]

        Find the len of the longest dimension of array
        or object with shape property that contains a __len__ method

        Args:
            array (object): object containing a shape
                property with a len method

        Returns:
            int: len of shape
    """
    obj_shape = obj.shape
    max_obj_shape = np.argmax(obj.shape)
    return obj.shape[max_obj_shape]


def len_dim_shape_axis(obj: object, axis=0) -> int:
    """len_dim_shape_axis

    Find the len of the dimension of array
    or object with shape property containing a __len__ method.
    Ferformed along specified axis

    Args:
        obj (object): [description]
        axis (int, optional): dimension to find the length of. Defaults to 0.

    Returns:
        int: [description]
    """
    return array.shape[axis]


class LenDimShape:

    def __init__(self, axis: Union[int, str]) -> None:
        """__init__

        get the length of an array along an axis, the object
        is assumed to have the property shape which in itself
        has a __len__ method

        Args:
            axis (Union[int, str]): axis by which to perform the check,
                can be either an integer or ['shortest', 'longest']
        """
        self.axis = axis
        self.set_dim_extractor()

    def __call__(self, obj: object) -> int:
        return self.dim_extractor(obj)

    def set_dim_extractor(self) -> None:
        if _is_string(self.axis):
            assert _in_aliases(axis), f"{axis} not in aliases"
            if _is_shortest(self.axis):
                self.dim_extractor = len_dim_shape_shortest
            elif _is_longest(self.axis):
                self.dim_extractor = len_dim_shape_longest
            else:
                raise Exception("setting dim extraction method failed")
        else:
            self.dim_extractor = partial(len_dim_shape_axis, axis=self.axis)
