try:
    from pymethods import arrays as _arrays
    from pymethods import math as _math
    from pymethods import utils as _utils
    from pymethods import pyplot as _plt
except ImportError:
    from .. import arrays as _arrays

import numpy as _np


class Ellipse(_arrays.Contour):

    def __new__(
        cls, r1, r2, *args,
        npts=100, center=None, flat=False, basis=None, **kwargs
    ):
        if center is None:
            center = _arrays.Vector(0, 0, 0)
        else:
            center = _arrays.Vector(center)

        theta = _np.linspace(-_np.pi, _np.pi, npts)
        x = r1*_np.cos(theta)
        y = r2*_np.sin(theta)

        if flat:
            return super().__new__(
                cls, x + center[0], y + center[0], *args, **kwargs)
        else:
            z = _np.zeros_like(x)
            if basis is None:
                return super().__new__(
                    cls, x + center[0], y + center[1], z + center[2],
                    *args, **kwargs
                )
            out = super().__new__(
                cls, x, y, z, *args, **kwargs).change_reference_frame(basis)
            out += center.column
            return out

    def __init__(self, *args, **kwargs):
        kwargs.pop("xshift", None)
        kwargs.pop("yshift", None)
        super().__init__(*args, **kwargs)


class Circle(Ellipse):

    @classmethod
    def from_two_points_and_normal(cls, p1, p2, normal, **kwargs):

        p1 = _arrays.Vector(p1).make_3d().squeeze()
        p2 = _arrays.Vector(p2).make_3d().squeeze()

        kk = _arrays.Vector(normal).hat.squeeze()
        jj = _arrays.Vector(p1.perpendicular(kk)).hat.squeeze()
        ii = _arrays.Vector(_np.cross(_np.array(jj), _np.array(kk))).hat

        basis = _arrays.Basis(ii, jj, kk)

        r     = (p2 - p1).magnitude()/2

        return cls(r, center=(p1+p2)/2, basis=basis, **kwargs)

    def __new__(cls, r, *args, **kwargs):
        return super().__new__(cls, r, r, *args, **kwargs)


class Trapezoid(_arrays.Contour):

    def __new__(cls, s1, s2, s3, s4, basis=None, corner=None, **kwargs):

        out = _np.concatenate(
            [s1, s2[:, 1:], s3[:, 1:], s4[:, 1:-1]], axis=1)

        if basis is not None:
            shift = _arrays.Vector(_math.contour_centroid(out)).column
            out -= shift
            out = _math.scalar_project(out, basis)
            out += shift

        if corner is not None:
            corner = _arrays.Vector(*corner).make_3d().make_column()
            out += corner

        return super().__new__(cls, out, **kwargs)

    @property
    def corner_indices(self):
        if not hasattr(self, "_corner_indices"):
            center = _math.contour_centroid(self).column
            distance = (self - center).magnitude()
            abs_dist_grad = _np.gradient(_np.gradient(distance))
            inds = _np.argsort(abs_dist_grad)
            corners = [0, *inds[0:3]]
            corners.sort()
            self._corner_indices = corners
        return self._corner_indices

    def scatter3d_corners(self, *args, color_coded=False, **kwargs):
        corners = self.corner_indices
        if color_coded:
            _plt.scatter3d(*self[:, corners[0]], c="g")
            _plt.scatter3d(*self[:, corners[1]], c="b")
            _plt.scatter3d(*self[:, corners[2]], c="b")
            return _plt.scatter3d(*self[:, corners[3]], c="r")
        else:
            return _plt.scatter3d(*self[:, corners])

    def corner_split(self, npts=100):
        output = []
        output.append(self(_np.linspace(self.sc0, self.sc1, npts)))
        output.append(self(_np.linspace(self.sc1, self.sc2, npts)))
        output.append(self(_np.linspace(self.sc2, self.sc3, npts)))
        output.append(self(_np.linspace(self.sc3, self.sc0, npts)))
        return output

    def transfinitable_corner_split(self, npts=100):
        output = []
        output.append(self(_np.linspace(self.s0, self.s1, npts)))
        output.append(self(_np.linspace(self.s1, self.s2, npts)))
        output.append(self(_np.linspace(self.s3, self.s2, npts)))
        output.append(self(_np.linspace(1, self.s3, npts)))
        return output

    @property
    def c0(self):
        return self.corner_indices[0]

    @property
    def c1(self):
        return self.corner_indices[1]

    @property
    def c2(self):
        return self.corner_indices[2]

    @property
    def c3(self):
        return self.corner_indices[3]

    @property
    def s0(self):
        return self.s_frac[self.c0]

    @property
    def s1(self):
        return self.s_frac[self.c1]

    @property
    def s2(self):
        return self.s_frac[self.c2]

    @property
    def s3(self):
        return self.s_frac[self.c3]


class RightAngleTrapezoid(Trapezoid):

    def __new__(
        cls, length_height, length_width, npts_height=100, npts_width=100,
        **kwargs
    ):

        height       = _np.linspace(0, length_height, npts_height)
        width        = _np.linspace(0, length_width , npts_width)
        zeros_height = _np.zeros_like(height)
        zeros_width  = _np.zeros_like(width)

        s1 = _arrays.Curve(width, zeros_width, zeros_width)
        s2 = _arrays.Curve(zeros_height + length_width, height, zeros_height)
        s3 = _arrays.Curve(_np.flipud(width), zeros_width + length_height, zeros_width)
        s4 = _arrays.Curve(zeros_height, _np.flipud(height), zeros_height)

        return super().__new__(cls, s1, s2, s3, s4, **kwargs)


class Square(RightAngleTrapezoid):

    def __new__(
        cls, length, *args, npts=100, **kwargs
    ):
        return super().__new__(
            cls, length, length, npts_height=npts, npts_width=npts, **kwargs)


    def __init__(self, length, *args, **kwargs):
        self.length = length
        super().__init__(*args, **kwargs)


class Rectangle(RightAngleTrapezoid):

    def __init__(self, height, width, *args, **kwargs):
        self.height = height
        self.width  = width
        super().__init__(*args, **kwargs)

class Decompose:

    def __init__(
        self, contour: _arrays.Contour, npts=100,
        c1=0.25, c2=0.5, c3=0.75
    ):
        self.s1 = contour(_np.linspace(0, c1, npts))
        self.s2 = contour(_np.linspace(c1, c2, npts))
        self.s3 = contour(_np.linspace(c2, c3, npts))
        self.s4 = contour(_np.linspace(c3, 1, npts))
        self.sections = [self.s1, self.s2, self.s3, self.s4]
        self.maxiter = 4


if __name__ == "__main__":

    import pymethods.pyplot as plt
    import pymethods.math as pmath
    import pymethods.arrays as pma

    basis   = pma.Basis(pma.Vector(1,0,0).rotation_matrix(45, units="d"))

    ellipse = Ellipse(1, 1, basis=basis, center=[1,1,1])

    square  = Square(1, 100, basis=basis)

    s1, s2, s3, s4 = square.transfinitable_corner_split()

    plt.plot_stream3d(s1, color="green")
    plt.plot_stream3d(s2, color="green")
    plt.plot_stream3d(s3, color="green")
    plt.plot_stream3d(s4, color="green")

    square.scatter3d_corners(color_coded=True)

    basis.quiver3d()
    ellipse.plot3d()

    plt.equal_aspect_3d()
    plt.show()