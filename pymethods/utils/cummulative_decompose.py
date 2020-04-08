import numpy as np
from typing import Iterable, List
from . import LockedDescriptor


def cummulative_decompose(iterable: Iterable) -> List:
    """cummulative_decompose

    decompose an itearble cummutavely, for example,
    cummulative_decompose('string') = ['s', 'st', 'str',...]

    Args:
        iterable (Iterable): an iterable object

    Returns:
        List: list of the cummulatively decomposed iterable
    """
    len_iterable = len(iterable)
    return [iterable[:i] for i in range(len_iterable) if len(iterable[:i]) > 0]


class IsSubsetString:
    case_sensitive = LockedDescriptor("_case_sensitive")

    __slots__ = ["_case_sensitive", "main_string", "_decomposed_string"]

    def __init__(self, main_string: str, case_sensitive=False):
        """__init__

        This class is used to check whether some input string is
        a subset of the given main_string

        Args:
            main_string (str): main string to check
            case_sensitive (bool, optional): set whether or not
                the check is case sensitive, this value cannot be changed
                once set. Defaults to False.
        """
        self._case_sensitive = case_sensitive
        if not self._case_sensitive:
            main_string = main_string.lower()
        self.main_string = main_string

    def __call__(self, string: str) -> bool:
        """__call__

        check whether the comparison_string is a subset
        of the main_string

        Args:
            string (str): checks whether string is in self.decomposed_string

        Returns:
            bool:
        """

        if string in self.main_string:
            return True
        return False

    def __repr__(self):
        return f"<IsSubsetString of {self.main_string} at {hex(id(self))}>"

    @property
    def decomposed_string(self):
        if not hasattr(self, "_decomposed_string"):
            self._decomposed_string = cummulative_decompose(
                self.main_string)
        return self._decomposed_string
