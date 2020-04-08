import numpy as np

try:
    from pymethods import utils
except:
    from .. import utils
from typing import Iterable

from functools import wraps

_in_radians = utils.IsSubsetString('radians')
_in_degrees = utils.IsSubsetString('degrees')


class Angle(np.ndarray):
    units = utils.LockedDescriptor('_units')
    __slots__ = ['_units']

    def __new__(cls, value: np.float, units='degrees', **kwargs) -> object:
        """Angle

        class to control the creation of angles

        Args:
            value (np.float): float to be converted into
                angle

        Returns:
            object: instantiated angle
        """
        out = np.asarray(value).view(cls)
        out._units = units
        return out

    def __init__(self, value: np.float, units='radians', **kwargs) -> None:
        if _in_radians(units):
            self._units = 'radians'
        if _in_degrees(units):
            self._units = 'degrees'

    def __array_finalize__(self, obj: object) -> object:
        if utils.is_none(obj):
            return None
        if hasattr(obj, '_units'):
            self._units = obj._units

    @property
    def rad(self) -> object:
        if self.units != 'radians':
            return Angle(self*np.pi/180, units='radians')
        if self.units == 'radians':
            return self

    @property
    def deg(self) -> object:
        if self.units != 'degrees':
            return Angle(self*180/np.pi, units='degrees')
        if self.units == 'degrees':
            return self

    @classmethod
    def deg_to_rad(cls, degrees: object) -> object:
        return cls(degrees, units='degrees').rad

    @classmethod
    def rad_to_deg(cls, radians: object) -> object:
        return cls(radians, units='radians').deg

    def __repr__(self):
        mem_loc = utils.hex_memory(self)
        strout = [f"<Angle object at {mem_loc}>",
                  f"'units': {self.units}",
                  f"'value': {self}"]

        return "\n".join(strout)

# angles are not bool after an operation
# thus we wrap comparison methods to
# convert to angle to bool


def _decorate_comparison_method(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        output = method(*args, **kwargs)
        return np.bool(output)
    return wrapper

for method in utils.comparison_methods:
    decorated_method = _decorate_comparison_method(getattr(Angle, method))
    setattr(Angle, method, decorated_method)


if __name__ == "__main__":
    A = Angle(10)
    print(A < 5)
    print((A < 5).__class__)
    B = np.array([1, 2, 3])[[A < 5, 0, 0]]
    print('done testing')
