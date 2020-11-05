
from collections import deque
import numpy as np
import scipy.interpolate as sci
try:
    from pymethods import arrays, math
except:
    from .. import arrays, math

class VectorSpline:
    def __init__(self, list_splines, name=None):
        self.list_splines = list_splines
        self.name = name
    def __call__(self, s, **kwargs):
        output = []
        for data in self.list_splines:
            output.append(
                sci.splev(s, data, **kwargs)
            )
        return np.stack(output, axis=0)

class FieldMixin:

    def __init__(self, *args, **kwargs):
        kwargs.pop("fields", {})
        self.field_funcs = deque()
        super().__init__(*args, **kwargs)

    def _splinify(self, reparam=None):
        super()._splinify(reparam=reparam)
        for key, f in self.fields.items():
            self.spline_data(f, "field_funcs", reparam=reparam, name=key)

    def sortByBasis(self, basis):
        sorted_args = math.argSortByBasis(self[:, :-1], basis)
        ii = sorted_args.astype(int)
        return self.__class__(
            self[:, :-1][:, ii],
            fields = dict(
                [
                    (key, f[:, :-1][:, ii]) for (key, f)
                    in self.fields.items()
                ]
            )
        )

    def reset_funcs(self):
        if self.dim_funcs:
            self.dim_funcs = deque()
        if self.field_funcs:
            self.field_funcs = deque()

    def initialize_funcs(self):
        self.dim_funcs = deque()
        self.field_funcs = deque()

    def initialize_class(self, s, **kwargs):
        return self.__class__(
            np.stack([f(s) for f in self.dim_funcs]),
            fields = dict(
                [(f.name, f(s)) for f in self.field_funcs]
            )
        )

    def initialize_column_vector(self, s):
        return arrays.ColumnVector([f(s) for f in self.dim_funcs])


    def spline_data(self, iterable_data, target_name, reparam=None, name=None):

        if reparam is None:
            s = self.s_frac
        else:
            s = reparam
            self.reset_funcs()

        spline_list = []

        for data in iterable_data:

            try:
                spline_func = sci.splrep(s, data, **self.splineparams)
                spline_list.append(spline_func)
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
                    spline_list.append(spline_func)
                except ValueError:
                    if len(y_unique) > 1:
                        pass
                    else:
                        raise Exception

        getattr(self, target_name).append(
            VectorSpline(spline_list, name=name)
        )

class FieldCurve(FieldMixin, arrays.Curve):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _splinify(self, *args, **kwargs):
        super()._splinify(*args, **kwargs)

    def reset_funcs(self, *args, **kwargs):
        super().reset_funcs(*args, **kwargs)

    def initialize_funcs(self, *args, **kwargs):
        super().initialize_funcs(*args, **kwargs)

    def initialize_class(self, *args, **kwargs):
        return super().initialize_class(*args, **kwargs)

    def initialize_column_vector(self, *args, **kwargs):
        return super().initialize_column_vector(*args, **kwargs)


class FieldContour(FieldMixin, arrays.Contour):

    def __new__(cls, *args, **kwargs):

        # new_fields = []

        for key in kwargs['fields'].keys():

            field = kwargs['fields'][key]

            if len(field.shape) == 1:
                kwargs['fields'][key] = np.array(field)[None,:]

        if not math.is_closed_curve(args[0]):
            for key in kwargs['fields'].keys():
                field = kwargs['fields'][key]

                kwargs['fields'][key] = np.concatenate(
                    [field, field[:,0, None]], axis = -1
                )


        out = super().__new__(cls, *args, **kwargs)

        out.fields = kwargs['fields']

        return out


    def __init__(self, *args, **kwargs):
        kwargs.pop("fields", {})
        super().__init__(*args, **kwargs)

    def _splinify(self, *args, **kwargs):
        super()._splinify(*args, **kwargs)

    def reset_funcs(self, *args, **kwargs):
        super().reset_funcs(*args, **kwargs)

    def initialize_funcs(self, *args, **kwargs):
        super().initialize_funcs(*args, **kwargs)

    def initialize_class(self, *args, **kwargs):
        return super().initialize_class(*args, **kwargs)

    def initialize_column_vector(self, *args, **kwargs):
        return super().initialize_column_vector(*args, **kwargs)
