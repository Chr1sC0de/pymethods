try:
    from pymethods import (arrays, math, utils)
except ImportError:
    from .. import arrays
    from .. import math
    from .. import utils
import numpy as np
from collections import deque
import scipy.interpolate as sci
import scipy.signal as ss
import pyvista as pv
from .. import pyplot as plt


class SplineFunc:

    def __init__(self, splrep):
        self.splrep = splrep

    def __call__(self, s, **kwargs):
        return sci.splev(s, self.splrep, **kwargs)


class Curve(arrays.Vectorspace):

    mode = 'fraction'

    delta = utils.NoInputFunctionAlias('delta_per_point', store=True)
    s = utils.NoInputFunctionAlias('arc_length_per_point', store=True)
    s_tot = utils.NoInputFunctionAlias('total_arc_length', store=True)
    s_frac = utils.NoInputFunctionAlias('fraction_per_point', store=True)

    def __init__(self, *args, normal=None, centroid=None, **kwargs) -> None:
        reparam_curve = kwargs.pop('reparam_curve', None)
        self._initialize_splineparams(**kwargs)
        self.initialize_funcs()
        self._splinify(reparam=reparam_curve)

    def _initialize_splineparams(self, **kwargs):
        self.splineparams = {
            'per': False,
            'k': 3,
            's': None
        }
        self.splineparams.update(
            kwargs
        )

    def delta_per_point(self) -> np.ndarray:
        return np.concatenate(
            [[[0]], math.l2_norm(np.diff(self, axis=-1))], axis=-1
        )

    def arc_length_per_point(self) -> np.ndarray:
        arcdistance = np.zeros(self.shape[-1])
        arcdistance = np.cumsum(self.delta_per_point())
        return arcdistance
    
    def curvature(self):
        sOriginal = self.s_frac 
        sEquallySpaced = np.linspace(0,1, self.shape[-1]*50)
        points = self(sEquallySpaced)
        dxdt = v = np.gradient(points, axis=1)
        dx2d2t = a = np.gradient(dxdt, axis=1)
        numerator = np.cross(dxdt, dx2d2t, axis=0)
        numerator = np.linalg.norm(numerator, axis=0)
        denominator = np.linalg.norm(dxdt, axis=0)**3
        kappa = numerator/denominator
        kappaHat = sci.interp1d(sEquallySpaced, kappa)(sOriginal)
        return kappaHat

    def total_arc_length(self) -> np.ndarray:
        return self.arc_length_per_point()[-1]

    def fraction_per_point(self) -> np.ndarray:
        s = self.arc_length_per_point()
        s_max = self.total_arc_length()
        return s/s_max

    def arc_length_at_fraction(self, fraction) -> np.ndarray:
        return self.total_arc_length() * fraction

    def fraction_at_arc_length(self, arc_length) -> np.ndarray:
        assert np.abs(arc_length) <= self.s_tot
        return arc_length/self.s_tot

    def transport_frames(self):
        return np.array(math.frennet_serret_with_transport(self))

    def oriented_transport_frames(self, origin, jVector, return_index=True):

        origin_id = np.argmin(math.l2_norm(
            self - arrays.ColumnVector(origin)
        ))

        transportFrames = self.transport_frames()
        ijk_self = arrays.Basis(transportFrames[origin_id])
        jVector = arrays.ColumnVector(jVector).hat
        projected = jVector.project_to_plane(ijk_self[:, -1])
        j_new = math.normalize(
            projected.change_reference_frame(ijk_self)).squeeze()
        z_new = np.array([0, 0, 1])
        ijk_new = arrays.Basis(
            math.normalize(math.cross(j_new, z_new)), j_new, z_new
        )
        newTransportFrames = np.zeros_like(transportFrames)
        for i, frame in enumerate(transportFrames):
            newTransportFrames[i] = arrays.Basis(frame @ ijk_new)
        if return_index:
            return newTransportFrames, origin_id
        else:
            return newTransportFrames

    def findPointPairsAtPerpendicularDistance(
        self, curve, distance=0, resolution=None, tolerance=0.1,
        getClosest=True
    ):
        pointPairs = []
        vtkCurve = pv.Spline(curve.T)
        if resolution is not None:
            interpolatedSelf = self(np.arange(0, 1, resolution))
        else:
            interpolatedSelf = self
        T = interpolatedSelf.transport_frames()[:, :, -1]
        minDistance = 10000
        minID = 10000
        for i, origin in enumerate(interpolatedSelf.T):
            slicedPoints = vtkCurve.slice(
                normal=T[i], origin=origin).points
            if len(slicedPoints) > 0:
                for point in slicedPoints:
                    perpDistance = np.linalg.norm(point - origin)
                    diffFromDesired = np.abs(perpDistance-distance)
                    if diffFromDesired < minDistance:
                        minDistance = diffFromDesired
                        minID = i
                    if diffFromDesired <= tolerance:
                        input_point = point.view(arrays.Vector).astype(
                                origin.dtype)
                        pointPairs.append(
                            {
                                'on_main': origin,
                                'on_input': input_point,
                                'error': diffFromDesired,
                                'vector': input_point - origin
                            }
                        )
        if len(pointPairs) == 0:
            print(
                f' the minimum distance {minDistance} for origin point {minID}')
        if len(pointPairs) != 0:
            if getClosest:
                pointPairs.sort(key=lambda x: x['error'])
                pointPairs = pointPairs[0]
        else:
            pass

        return pointPairs

    def _splinify(self, reparam=None):

        if reparam is None:
            s = self.s_frac
        else:
            s = reparam
            self.reset_funcs()

        for i in range(self.shape[0]):
            try:
                spline_func = sci.splrep(s, self[i], **self.splineparams)
                self.dim_funcs.append(SplineFunc(spline_func))
            except ValueError:
                try:
                    y_unique, unique_inds = np.unique(
                        self[i][0:-2], return_index=True)
                    unique_inds.sort()
                    s_unique = np.concatenate(
                        [s[unique_inds], s[-1, None]])
                    y_unique = np.concatenate(
                        [y_unique, self[i][-1, None]])
                    spline_func = sci.splrep(
                        s_unique, y_unique, **self.splineparams)
                    self.dim_funcs.append(SplineFunc(spline_func))
                except ValueError:
                    if len(y_unique) > 1:
                        pass
                    else:
                        raise Exception

    def spline_data(self, data, target_name, reparam=None):

        if reparam is None:
            s = self.s_frac
        else:
            s = reparam
            self.reset_funcs()

        try:
            spline_func = sci.splrep(s, data, **self.splineparams)
            getattr(self, target_name).append(SplineFunc(spline_func))
        except ValueError:
            try:
                y_unique, unique_inds = np.unique(
                    data[0:-2], return_index=True)
                unique_inds.sort()
                s_unique = np.concatenate(
                    [s[unique_inds], s[-1, None]])
                y_unique = np.concatenate(
                    [y_unique, data[-1, None]])
                spline_func = sci.splrep(
                    s_unique, y_unique, **self.splineparams)
                getattr(self, target_name).append(SplineFunc(spline_func))
            except ValueError:
                if len(y_unique) > 1:
                    pass
                else:
                    raise Exception

    def reset_funcs(self):
        if self.dim_funcs:
            self.dim_funcs = deque()

    def initialize_funcs(self):
        self.dim_funcs = deque()

    def initialize_class(self, s, **kwargs):
        return self.__class__(np.stack([f(s) for f in self.dim_funcs]), **kwargs)

    def initialize_column_vector(self, s):
        return arrays.ColumnVector([f(s) for f in self.dim_funcs])

    def filter(self, window_length, polyorder, **kwargs):
        self = self.view(np.ndarray)
        return self.__class__(
            ss.savgol_filter(self, window_length, polyorder, **kwargs))

    def __call__(
            self, s, *args, reparam_curve=None, **kwargs) -> np.ndarray:
        try:
            if not hasattr(self, 'dim_funcs'):
                self._initialize_splineparams(**kwargs)
                self.initialize_funcs()
                self._splinify()

            if reparam_curve is None:
                param_curve = self
            else:
                self._splinify(reparam=reparam_curve)

            if self.mode in 'arclength':
                s = s/param_curve.s_tot

            s = np.array(s)

            assert all([s.max() <= 1, s.min() >= -1])

            if utils.is_iterable(s):
                s[s < 0] = s[s < 0] + 1
            return self.initialize_class(s)
        except ValueError:
            return self.initialize_column_vector(s)

    def to_vtk(self):
        return pv.Spline(self.T)


class Contour(Curve):

    area = utils.NoInputFunctionAlias('calc_area', store=True)
    centroid = utils.NoInputFunctionAlias('calc_centroid', store=True)
    basis = utils.NoInputFunctionAlias('calc_basis', store=True)
    normal = utils.NoInputFunctionAlias('calc_normal', store=True)

    def __new__(cls, *args, write_end=False,  **kwargs):
        out = super().__new__(cls, *args, **kwargs)
        return math.close_curve(out, write_end=write_end).view(cls)

    def _initialize_splineparams(self, write_end=False, **kwargs):
        self.write_end = write_end
        self.splineparams = {
            'per': True,
            'k': 3,
            's': None
        }
        self.splineparams.update(
            kwargs
        )

    def calc_area(self):
        return math.area(self)

    def calc_centroid(self):
        return arrays.ColumnVector(math.contour_centroid(self))

    def calc_normal(self):
        centered = self - self.centroid
        return arrays.ColumnVector(
            math.approximate_normal(centered)
        )

    def __call__(
            self, s, *args, reparam_curve=None,
            close=True, **kwargs) -> np.ndarray:

        if not hasattr(self, 'dim_funcs'):
            self._initialize_splineparams(**kwargs)
            self.initialize_funcs()
            self._splinify()

        if reparam_curve is None:
            param_curve = self
        else:
            param_curve = Curve(reparam_curve)

        if self.mode in 'arclength':
            s = s/param_curve.s_tot

        s = np.array(s)

        assert all([s.max() <= 1, s.min() >= -1])

        if utils.is_iterable(s):
            s[s < 0] = s[s < 0] + 1

        if any(
            [s[0] != 0, s[-1] != 1]
        ):
            close = False

        if close:
            return self.initialize_class(s, write_end=self.write_end)
        else:
            return Curve(np.stack([f(s) for f in self.dim_funcs]))

    def filter(
            self, window_length, polyorder, mode='wrap', retries=10, **kwargs):

        original_class = self.__class__
        self = self.view(np.ndarray)
        signals = []
        rolls = np.linspace(
            len(self.T), retries
        )
        for roll in rolls:
            roll = int(roll)
            rolled = np.roll(self, roll, -1)
            filtered = ss.savgol_filter(
                rolled, window_length, polyorder, mode=mode, **kwargs)
            unrolled = np.roll(filtered, -roll, -1)
            signals.append(unrolled)
        mean = np.mean(signals, 0)
        return original_class(mean)

    def calc_basis(self):
        i = math.normalize(self[:, 0, None] - self.centroid).squeeze()
        k = self.calc_normal()
        j = math.normalize(math.cross(k, i))
        return arrays.Basis(i.squeeze(), j.squeeze(), k.squeeze())

    def argSortByBasis(self, basis):
        return math.argSortByBasis(self, basis)

    def sortByBasis(self, basis):
        sorted_args = math.argSortByBasis(self[:, :-1], basis)
        return self.__class__(self[:, :-1][:, sorted_args.astype(int)])

    @classmethod
    def circle(cls, r, npts=100, centroid='origin'):
        if centroid == 'origin':
            centroid = np.zeros((2, 1))

        theta = np.linspace(-np.pi, np.pi, npts)

        x = r*np.cos(theta)
        y = r*np.sin(theta)

        return cls(np.stack([x, y], axis=0)).make_3d() + arrays.ColumnVector(centroid).make_3d()

    def area_assumed_diameter(self):
        return 2*np.sqrt(self.area/np.pi)

    # def make2d(self, returnBackwards=True):
    #     centroid = self.centroid
    #     basis = self.basis

    #     if returnBackwards:
    #         return transformed, (centroid, basis)


class FlatContour(Contour):
    """FlatContour
        Flat contours are 3d contours which exist on a plane specified by a
        normal. Note: The contour is automatically converted to 3d
    """
    def __new__(cls, *args, normal=None, centroid=None, **kwargs):

        out = super().__new__(cls, *args, **kwargs)
        if centroid is None:
            try:
                centroid = out.centroid
                centered = out - centroid
            except:
                temp = np.zeros((centroid.shape[0], out.shape[-1] ))
                temp[:out.shape[0]] = out
                out = temp
                out = super().__new__(cls, out, **kwargs)
                centroid = out.centroid
                centered = out - centroid
        else:
            try:
                centered = out - centroid
            except:
                temp = np.zeros((centroid.shape[0], out.shape[-1] ))
                temp[:out.shape[0]] = out
                out = temp
                out = super().__new__(cls, out, **kwargs)
                centered = out - centroid

        if normal is None:
            normal = math.approximate_normal(centered)
        normal = arrays.ColumnVector(normal)
        to_plane = centered - normal @ (centered.T @ normal).T
        return math.close_curve(to_plane+centroid).view(cls)

    def get_normal(self):
        k_test = math.approximate_normal(self-self.centroid)
        i = math.normalize(self[:, 0, None] - self.centroid)
        n = math.normalize(
            self[:, self.shape[-1]//4, None] - self.centroid)
        k_test = math.normalize(
            math.cross(i, n))
        j_test = math.cross(k_test, i)
        alpha1 = math.smallest_angle_between_vectors(j_test, n)
        alpha2 = math.smallest_angle_between_vectors(-j_test, n)
        if alpha1 < alpha2:
            return arrays.Vector(math.normalize(k_test))
        else:
            return arrays.Vector(math.normalize(-k_test))





if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    f = plt.figure()
    ax = f.add_subplot(111, projection='3d')

    if False:
        x = y = z = np.linspace(0, 10, 10)
        curve = Curve(x, y, z)
        interp_curve = curve(
            np.linspace(0, 1, 100)
        )

        ax.scatter(*interp_curve)
        plt.show()

    if False:
        theta = np.linspace(-np.pi, np.pi, 10000)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        contour = Contour(x, y).make_3d() + arrays.ColumnVector(1, 2, 3)

        normal = contour.normal

        area = contour.area
        true_area = np.pi*r**2

        contour_centroid = contour.centroid()

        contour_interp = contour(
            np.linspace(0, 1, 100)
        )

        ax.scatter(*contour)
        ax.scatter(*contour_interp, color='red')
        ax.scatter(*contour_centroid, color='orange')

        plt.show()

    if False:
        theta = np.linspace(-np.pi, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.zeros_like(x)

        contour = Contour(x, y, z)
        contour_flat = FlatContour(x, y, z, normal=[1, 1, -10])
        ax.scatter(*contour)
        ax.scatter(*contour_flat)
        plt.show()

    if True:
        circle = Contour.circle(1, npts=100)

        circle.plot3d()

        def transfinite_interpolation(contour, ptsOnSegment=25):
            contour = Contour(contour)
            c_1 = Curve(
                contour(np.linspace(0, 0.25, ptsOnSegment))
            )
            c_4 = Curve(
                contour(np.linspace(0.25,0.5,ptsOnSegment))
            )
            c_3 = Curve(
                np.fliplr(np.array(contour(np.linspace(0.5,0.75,ptsOnSegment))))
            )
            c_2 = Curve(
                np.fliplr(np.array(contour(np.linspace(0.75,1.0,ptsOnSegment))))
            )

            p_12 = c_1[:, 0, None]
            p_34 = c_3[:, -1, None]
            p_14 = c_1[:, -1, None]
            p_32 = c_2[:, -1, None]

            p_12.scatter3d(color='green')
            c_1.scatter3d(color='green')
            p_34.scatter3d(color='blue')
            c_3.scatter3d(color='blue')
            p_14.scatter3d(color='orange')
            c_4.scatter3d(color='orange')
            p_32.scatter3d(color='red')
            c_2.scatter3d(color='red')

            def S(u,v):
                plus = (1-v) * c_1(u) + v * c_3(u) + (1 - u) * c_2(v) + u * c_4(v)

                minus = (1-u)*(1-v) * p_12 + u*v*p_34 + u*(1-v)*p_14 + (1-u)*v*p_32

                return plus -  minus

            return S

        S = transfinite_interpolation(circle)

        x,y = 10, 10

        X, Y = np.meshgrid(
            np.linspace(0, 1, x), np.linspace(0, 1, y)
        )
        U = X.flatten()
        V = Y.flatten()

        domain = S(U, V)

        structured_domain = domain.reshape((3, x, y))

        # mesh = pv.StructuredGrid(*structured_domain)
        # mesh.plot(show_bounds =True)
