try:
    from pymethods.parse.angiography import Folder as _Folder
    from pymethods.arrays.structured import CylindricalSurface as _CylindricalSurface
except:
    from ...parse.angiography import Folder as _Folder
    from ...parse.arrays.structured import CylindricalSurface as _CylindricalSurface


class Base(_Folder):

    centerline_id = None
    contour_id = None

    def construct(
            self, npts_longitudinal=200, npts_contour=50, **filter_kwargs):
        centerline = getattr(self, self.centerline_id).data
        contours = getattr(self, self.contour_id).data

        artery_surface = _CylindricalSurface.from_contours(contours)
        artery_surface = artery_surface.interpolate_long(
            npts_longitudinal, reparam_curve=centerline.s_frac)
        artery_surface = artery_surface.filter(**filter_kwargs)
        artery_surface = artery_surface.interpolate_contours(npts_contour)
        return artery_surface


class Meta:

    def __new__(cls, vesselName, centerline_id, contour_id):
        return type('%sVessel' % vesselName, (Base, ), {
                'centerline_id': centerline_id,
                'contour_id': contour_id
            }
        )


Main  = Meta('Main', 'bifCenterline1', 'CrossSectionEllipseSet1')
Bifur = Meta('Bifur', 'bifCenterline2', 'CrossSectionEllipseSet2')

