import pathlib as pt
import pymethods as pma
import logging
import numpy as np

centerlineMethods = {
    'A': 'CenterlinesA',
    'B': 'CenterlinesB'
}


class VesselSurface:

    def __init__(
            self, main_path, oct_name='oct',
            angiography_name='angiography'):
        main_path = pt.Path(main_path)
        self.path_angio = pt.Path(main_path)/angiography_name
        self.path_oct = pt.Path(main_path)/oct_name
        self.path_main = main_path

    def construct(
                self,
                *,
                mm_per_pixel,
                mm_per_frame,
                processors=4,
                centerline_type='A',
                contour_window=13,
                interpolate_contours=360,
                centerlineResolution=0.001,
                **kwargs
            ):

        folder_angio = getattr(pma.parse.angiography,
                               centerlineMethods[centerline_type])(
                                   self.path_angio)

        centerline_main, centerline_bifur = folder_angio.parse(
                                   resolution=centerlineResolution).values()

        try:
            folder_oct = pma.parse.ivoct.Folder(self.path_oct)
            folder_oct.load()
        except ValueError:
            logging.info('OCT data not found, running oct.parse()')
            folder_oct.parse(processors=processors)

        contours, landmark, frame_id, image_files, landmark_path =\
            folder_oct.data_scaled(mm_per_pixel).values()

        perpendicularPointDict = \
            centerline_main.findPointPairsAtPerpendicularDistance(
                centerline_bifur, distance=landmark.bar, resolution=0.0001)

        pt_main, pt_bifur, error, vector = perpendicularPointDict.values()

        origin_id = np.argmin(
            pma.math.l2_norm(
                centerline_main - pma.arrays.ColumnVector(pt_main))
        )

        s_location_landmark = centerline_main.s_frac[origin_id]

        frac_per_frame = mm_per_frame/centerline_main.s_tot

        distal_half = pma.utils.gap_space(
            s_location_landmark, 0, frac_per_frame)
        proximal_half = pma.utils.gap_space(
            s_location_landmark, 1, frac_per_frame)[:-1]

        interpolated_landmark = len(distal_half)

        s_req = np.concatenate(
            [distal_half, proximal_half[1:]]
        )
        s_req.sort()
        interpolated_centerline = centerline_main(s_req)

        centerline_start = interpolated_landmark-frame_id
        centerline_end = centerline_start + len(contours)

        assert centerline_start > -1, 'not enough distal centerline'
        assert centerline_end < interpolated_centerline.shape[-1], \
            'not enough centerline proximally'

        transportFrames, origin_id = \
            interpolated_centerline.oriented_transport_frames(
                interpolated_centerline[:, interpolated_landmark, None],
                vector)

        translated_contours = []

        ids_centerline = []

        for j, i in enumerate(range(centerline_start, centerline_end)):
            contour = contours[j]
            contour = pma.math.make_3d(contour)
            contour = pma.arrays.Contour(contour).filter(contour_window, 3)
            contour = contour(np.linspace(0, 1, interpolate_contours))
            contour = contour - contour.centroid

            origin = interpolated_centerline[:, i].make_column()
            basis = transportFrames[i]
            contour = (basis @ contour) + origin

            translated_contours.append(contour)
            ids_centerline.append(i)

        surface = pma.arrays.structured.CylindricalSurface.from_contours(
            translated_contours)

        surface = self.surfaceClean(surface, **kwargs)

        self.required_centerline = interpolated_centerline[:, ids_centerline]
        self.required_basis = transportFrames[ids_centerline]

        self.surface = surface

        return surface

    def surfaceClean(
            self, surface, surface_filter=25,
            interpolate_long=720, surface_contour_interp=360):

        surface = surface.interpolate_long(interpolate_long)
        surface = surface.filter(window_size=surface_filter)
        surface = surface.interpolate_contours(surface_contour_interp)
        return surface

    def save(
            self, filenameSurface='surface.vtk',
            filenameCenterlinesRotations='centerlineAndRotations'):

        self.surface.to_vtk(self.path_main/filenameSurface)

        np.savez(
            self.path_main/filenameCenterlinesRotations,
            centerline=self.required_centerline,
            basis=self.required_basis
        )


if __name__ == "__main__":
    path = pt.Path(r'D:\Github\pymethods\testsReconstruction\test_1')
    reconstruction = VesselSurface(path)
    reconstruction.construct(
        mm_per_pixel=0.009356,
        mm_per_frame=0.2).to_vtk().plot()
