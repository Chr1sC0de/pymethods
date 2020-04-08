import abc
from typing import Iterable, Union, Generic
import numpy as np


class IsAny:
    __slots__ = ['comaprison_objects']

    def __init__(
            self, *comaprison_objects: Iterable[Union[type, object]]) -> None:
        """__init__

        base class is Is classes. Is classes are initialized with an iterable
        of either objects or types. The call to the class will perform a
        comparison check on the input using the objects or types stored
        in the initialization. For examples Isinstance(str, list)(obj)
        will check whether or not the obj is an instance of a string or
        a list

        Args:
            comparison_objects (Iterable[Union[type, object]]):
                an iterable containing objects
        """
        self.comaprison_objects = comaprison_objects

    def __call__(self, obj: object) -> bool:
        """__call__

        using the self.check method, test the input obj
        on each of the elements of self.comaprison_objects.
        If one instance is true return true

        Args:
            obj (object): arbitrary object to be tested

        Raises:
            NotImplementedError: check must be implemented

        Returns:
            bool: True if obj passes check for one of
                self.comaprison_objects
        """
        for comp in self.comaprison_objects:
            if self.check(obj, comp):
                return True
        return False

    @abc.abstractmethod
    def check(self, obj: object, comparison: type) -> bool:
        """check

        abstract method that compares obj to comparison,

        Args:
            obj (object): object to be checked
            comparison (type): type to compare with

        Raises:
            NotImplementedError:

        Returns:
            bool: True if passes checks else False
        """
        raise NotImplementedError


class IsAll(IsAny):
    def __call__(self, obj: object) -> bool:
        """__call__

        using the self.check method, test the input obj
        on each of the elements of self.comaprison_objects.
        If one instance is true return true

        Args:
            obj (object): arbitrary object to be tested

        Raises:
            NotImplementedError: check must be implemented

        Returns:
            bool: True if obj passes check for one of
                self.comaprison_objects
        """
        for comp in self.comaprison_objects:
            if self.check(obj, comp):
                return False
        return True


class Isin(IsAny):
    def check(self, obj: object, comparison: Iterable) -> bool:
        """Isinany

        check if the object is in any of the self.comaprison_objects

        Args:
            IsAny ([type]): [description]
            obj (object): [description]
            comparison (Iterable): [description]

        """
        return obj in comparison


class Isinstance(IsAny):
    def check(self, obj: object, comparison: type) -> bool:
        """Isinstance

        test if obj is an instance of the comparison type

        Args:
            obj (object): object to be checked
            comparison (type): type to compare with

        Returns:
            bool: True if instance
        """
        return isinstance(obj, comparison)


class Issubclass(IsAny):
    def check(self, obj: object, comparison: type) -> bool:
        """Issubclass

        test if obj is a subclass of the comparison type

        Args:
            obj (object): object to be checked
            comparison (type): type to compare with

        Returns:
            bool: True if subclass
        """
        return issubclass(obj.__class__, comparison)


def is_none(obj: object) -> bool:
    """is_none

    check if the obj is None

    Args:
        obj (object):

    Returns:
        bool: True if None
    """
    if obj is None:
        return True
    return False

is_iterable = Isinstance(Iterable)
is_string = Isinstance(str)
is_int = Isinstance(int, np.int)
