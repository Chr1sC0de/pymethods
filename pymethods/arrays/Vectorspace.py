from ..arrays import (
    Basis
)
from .. import math
import numpy as np
from .. import utils
import typing
from typing import Union


class Vectorspace(Basis):
    normal = utils.NoInputFunctionAlias('calc_normal', store=True)

    @classmethod
    def _parse_single_arg(cls, array: np.ndarray) -> np.ndarray:
        out = np.array(array)
        assert utils.len_shape(out) == 2, \
            "The lenshape of the input must be 2"
        out = np.asarray(out)
        return out

    def calc_normal(self):
        return math.approximate_normal(self)

    def least_squares_fitting_of_two_point_sets(
            self, vectorspace: np.ndarray) -> Union[np.ndarray, np.float]:
        R, t = math.least_squares_fitting_of_two_point_sets(self, vectorspace)
        return R, t

    @classmethod
    def _parse_star_arg(
            cls, args: typing.Iterable[typing.Iterable]) -> np.ndarray:
        return np.stack(
            args, axis=0
        )

    @classmethod
    def _new_hook_post_parse(self, out):
        return out

    def quiverly(self, *args, **kwargs):
        NotImplementedError()

