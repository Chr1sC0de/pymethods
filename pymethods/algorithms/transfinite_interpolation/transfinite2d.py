from . transfinite_domain import TransfiniteDomain
from pymethods.arrays import Contour, Curve, Vectorspace
import numpy as np


class Transfinite2d(TransfiniteDomain):

    def __init__(self, contour, refinement=None):
        assert isinstance(contour, Contour)
        self._contour = contour
        if refinement is None:
            refinement = contour.shape[-1]//4
        # c_1 = Curve(contour(np.linspace(0, 0.25, refinement)))
        # c_4 = Curve(contour(np.linspace(0.25, 0.5, refinement)))
        # c_3 = Curve(np.fliplr(np.array(contour(np.linspace(0.5, 0.75, refinement)))))
        # c_2 = Curve(np.fliplr(np.array(contour(np.linspace(0.75, 1.0, refinement)))))
        # super().__init__(c_1, c_2, c_3, c_4)
        c_1 = Curve(contour(np.linspace(0, 0.25, refinement)))
        c_2 = Curve(contour(np.linspace(0.25, 0.5, refinement)))
        c_3 = Curve(np.fliplr(np.array(contour(np.linspace(0.5, 0.75, refinement)))))
        c_4 = Curve(np.fliplr(np.array(contour(np.linspace(0.75, 1.0, refinement)))))
        super().__init__(c_1, c_2, c_3, c_4)


    @property
    def contour(self):
        return self._contour.copy()