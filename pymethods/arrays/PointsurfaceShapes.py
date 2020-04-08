try:
    from pymethods import arrays as ent
    from pymethods import pyplot as plt
except ImportError:
    from .. import arrays as ent
    from .. import pyplot as plt

import numpy as np
import inspect
from functools import wraps
import abc


class CacheValue:

    def __init__(self, name):
        self.item_name = name

    def __call__(self, function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            if not hasattr(obj, self.item_name):
                value = function(obj, *args, **kwargs)
                setattr(obj, self.item_name, value)
            return getattr(obj, self.item_name)
        return wrapper


class _SurfaceProperties:

    def __init__(self, xyz, *args, external=True):
        arg_names = inspect.getfullargspec(self.__init__).args[2:]
        for value, name in zip(args, arg_names):
            setattr(self, name, value)
        self.x, self.y, self.z = xyz
        self.solve()
        if external:
            self._gaussian_curvature *= -1
            self._maximum_curvature *= -1
            self._maximum_radii_of_curvature *= -1
            self._mean_curvature *= -1
            self._minimum_curvature *= -1
            self._minimum_radii_of_curvature *= -1
            tmp = self._maximum_curvature
            self._maximum_curvature = self._minimum_curvature
            self._minimum_curvature = tmp

    @abc.abstractproperty
    def gaussian_curvature(self):
        NotImplementedError

    @abc.abstractproperty
    def mean_curvature(self):
        NotImplementedError

    @abc.abstractproperty
    def maximum_radii_of_curvature(self):
        NotImplementedError

    @abc.abstractproperty
    def minimum_radii_of_curvature(self):
        NotImplementedError

    @property
    @CacheValue('_minimum_curvature')
    def minimum_curvature(self):
        return 1 / self.R_1

    @property
    @CacheValue('_maximum_curvature')
    def maximum_curvature(self):
        return 1 / self.R_2

    @property
    def k_1(self):
        return self.maximum_curvature

    @property
    def k_2(self):
        return self.minimum_curvature

    @property
    def R_1(self):
        return self.maximum_radii_of_curvature

    @property
    def R_2(self):
        return self.minimum_radii_of_curvature

    @property
    def H(self):
        return self.mean_curvature

    @property
    def K(self):
        return self.gaussian_curvature

    def solve(self):
        self.K
        self.H
        self.k_1
        self.k_2
        self.R_1
        self.R_2


class EllipsoidSurfaceProperties(_SurfaceProperties):

    a = 1
    b = 1
    c = 1

    def __init__(self, xyz, a, b, c, **kwargs):
        super().__init__(xyz, a, b, c, **kwargs)

    @property
    @CacheValue('_gaussian_curvature')
    def gaussian_curvature(self):
        abc = self.a * self.b * self.c
        x_ = (self.x ** 2) / (self.a ** 4)
        y_ = (self.y ** 2) / (self.b ** 4)
        z_ = (self.z ** 2) / (self.c ** 4)
        denominator = (abc * (x_ + y_ + z_)) ** 2
        return 1/denominator

    @property
    @CacheValue('_mean_curvature')
    def mean_curvature(self):
        x, y, z = self.x, self.y, self.z
        a, b, c = self.a, self.b, self.c
        abc = a * b * c
        x_ = (x ** 2) / (a ** 4)
        y_ = (y ** 2) / (b ** 4)
        z_ = (z ** 2) / (c ** 4)
        numerator = np.abs(
            (x ** 2) + (y ** 2) + (z ** 2)
            - (a ** 2) - (b ** 2) - (c ** 2)
        )
        denominator = 2 * (abc ** 2) * (
            x_ + y_ + z_) ** (3/2)
        return numerator / denominator

    @property
    @CacheValue('_maximum_radii_of_curvature')
    def maximum_radii_of_curvature(self):
        B = self.H ** 2 - self.K
        if not np.isclose(np.sum(B), 0):
            B = np.sqrt(B)
        denominator = self.H - B
        return 1 / denominator

    @property
    @CacheValue('_minimum_radii_of_curvature')
    def minimum_radii_of_curvature(self):
        B = self.H ** 2 - self.K
        if not np.isclose(np.sum(B), 0):
            B = np.sqrt(B)
        denominator = self.H + B
        return 1 / denominator


class CylinderSurfaceProperties(_SurfaceProperties):

    def __init__(self, xyz, a, u, **kwargs):
        super().__init__(xyz, a, u, **kwargs)

    @property
    @CacheValue('_gaussian_curvature')
    def gaussian_curvature(self):
        return np.zeros_like(self.x)

    @property
    @CacheValue('_mean_curvature')
    def mean_curvature(self):
        return np.ones_like(self.x) * 1 / (2 * self.a)

    @property
    @CacheValue('_maximum_radii_of_curvature')
    def maximum_radii_of_curvature(self):
        return np.ones_like(self.x) * np.inf

    @property
    @CacheValue('_minimum_radii_of_curvature')
    def minimum_radii_of_curvature(self):
        return np.ones_like(self.x) * self.a


class TorusSurfaceProperties(_SurfaceProperties):

    def __init__(self, xyz, a, c, theta, phi, **kwargs):
        super().__init__(xyz, a, c, theta, phi, **kwargs)

    @property
    @CacheValue('_gaussian_curvature')
    def gaussian_curvature(self):
        return np.cos(self.theta)\
            / (self.a * (self.c + self.a * np.cos(self.theta)))

    @property
    @CacheValue('_mean_curvature')
    def mean_curvature(self):
        return (self.c + 2 * self.a * np.cos(self.theta))\
             / (2 * self.a * (self.c + self.a * np.cos(self.theta)))

    @property
    @CacheValue('_maximum_curvature')
    def maximum_curvature(self):
        return (self.H + np.sqrt(self.H ** 2 - self.K))

    @property
    @CacheValue('_minimum_curvature')
    def minimum_curvature(self):
        return (self.H - np.sqrt(self.H ** 2 - self.K))

    @property
    @CacheValue('_maximum_radii_of_curvature')
    def maximum_radii_of_curvature(self):
        return 1 / self.minimum_curvature

    @property
    @CacheValue('_minimum_radii_of_curvature')
    def minimum_radii_of_curvature(self):
        return 1 / self.maximum_curvature


class Ellipsoid(ent.Pointsurface):

    @classmethod
    def sunflower_spiral(cls, a=1, b=1, c=1, n_pts=1000, **kwargs):
        assert a > 0
        assert b > 0
        assert c > 0

        indices = np.arange(0, n_pts, dtype=np.float) + 0.5
        phi = np.arccos(1 - 2 * indices / n_pts)
        theta = np.pi * (1 + 5 ** 0.5) * indices
        xyz = (a * np.cos(theta) * np.sin(phi),
               b * np.sin(theta) * np.sin(phi),
               c * np.cos(phi))
        xyz = np.array(xyz)
        obj = cls(xyz, **kwargs)
        analytical = EllipsoidSurfaceProperties(
            xyz, a, b, c, external=kwargs.get('external', True)
        )
        obj.analytical = analytical
        return obj


class Sphere(Ellipsoid):

    @classmethod
    def sunflower_spiral(cls, r=1, n_pts=1000, **kwargs):
        return super(Sphere, cls).sunflower_spiral(
            a=r, b=r, c=r, n_pts=n_pts, **kwargs
        )


class Cylinder(ent.Pointsurface):

    @classmethod
    def sunflower_spiral(cls, a=1, u=5, n_pts=1000, **kwargs):
        indices = np.arange(0, n_pts, dtype=np.float)
        z = (indices + 0.5) / n_pts * u
        theta = np.pi * (5 ** 0.5 - 1) * indices
        x = a * np.cos(theta)
        y = a * np.sin(theta)
        xyz = np.array([x, y, z])
        obj = cls(xyz, **kwargs)
        analytical = CylinderSurfaceProperties(
            xyz, a, u, external=kwargs.get('external', True)
        )
        obj.analytical = analytical
        return obj

    @classmethod
    def z_and_r(cls, r=1, z=5, z_pts=200, theta_pts=60, **kwargs):
        theta = np.linspace(0, 2 * np.pi, theta_pts)
        z = np.linspace(0, z, z_pts)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        array = np.zeros((3, z_pts*theta_pts))
        for i, z_ in enumerate(z):
            i_start = theta_pts * i
            i_end = i_start + theta_pts
            array[0, i_start: i_end] = x
            array[1, i_start: i_end] = y
            array[2, i_start: i_end] = z_
        obj = cls(array, **kwargs)
        analytical = CylinderSurfaceProperties(
            obj, r, z, external=kwargs.get('external', True)
        )
        obj.analytical = analytical
        return obj


class Torus(ent.Pointsurface):
    @classmethod
    def sunflower_spiral(cls, a=1, c=5, n_pts=1000, **kwargs):
        indices = np.arange(0, n_pts, dtype=np.float) + 0.5
        phi = (indices + 0.5) / n_pts * 2 * np.pi
        theta = np.pi * (5 ** 0.5 - 1) * indices

        x = (c + a * np.cos(theta)) * np.cos(phi)
        y = (c + a * np.cos(theta)) * np.sin(phi)
        z = a * np.sin(theta)

        xyz = np.array([x, y, z])
        obj = cls(xyz, **kwargs)
        analytical = TorusSurfaceProperties(
            obj, a, c, theta, phi, external=kwargs.get('external', True)
        )
        obj.analytical = analytical
        return obj


if __name__ == "__main__":
    psurf = Ellipsoid.sunflower_spiral(
        n_pts=10000, a=2, leafsize=100, neighbours=150, external=False)
    # psurf = Cylinder.sunflower_spiral(
    #     n_pts=10000, neighbours=12, external=False)
    # psurf = Torus.sunflower_spiral(
    #     n_pts=50000, neighbours=300, external=False)
    psurf.plot_analytical_curvature()
    plt.show()
    psurf.compute_principle_curvatures(n_processors=10)
    psurf.check_normals_n_at_a_time(interval=500)
    psurf.plot_error()
    psurf.plot_analytical_curvature()
    psurf.plot_curvature()
    plt.show()
    print('done')
