# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import sys
import pymethods as pma
import pymethods.pyplot as plt
import pathlib as pt
import numpy as np
from time import time
import matplotlib

if __name__ == "__main__":

    cwd = pt.Path(__file__).parent

    # %%
    path_angio = pt.Path(cwd/r'../../Datasets/test_1/angiography')
    path_oct = pt.Path(cwd/r'../../Datasets/test_1/oct')

    # notice how we use the CenterlinesA to parse the centerlines. This ensures that the centerlines are oriented correctly
    folder_angio = pma.parse.angiography.CenterlinesA(path_angio)
    folder_oct = pma.parse.ivoct.Folder(path_oct)
    try:
        folder_oct.load()
    except:
        folder_oct.parse(processors=8)
    # %% [markdown]
    # let us first extract the necessary angiography data
    # %% [markdown]
    # ## Orienting the centerlines

    # %%
    centerline_main, centerline_bifur = folder_angio.parse().values()

    # %% [markdown]
    # We must note that the CenterlinesA and the CenterlinesB class both contain a parse method which orients the centerlines, bifCenterlines 1 and 2 and centerlines 1 and 2 respectively. We see that the centerlines are now ordered distal to proximal

    # %%
    plt.figure_3d()
    centerline_main.plot3d('g')
    main_tangents = centerline_main.transport_frames()[:, :, -1]
    centerline_bifur.plot3d('r')
    transportFrames = centerline_main.transport_frames()

    for i, (center, frame) in enumerate(zip(centerline_main.T, transportFrames)):
        if i%50 == 0:
            pma.arrays.ColumnVector(frame[:, -1]).quiver3d(origin=center)

    transportFrames = centerline_bifur.transport_frames()
    for i, (center, frame) in enumerate(zip(centerline_bifur.T, transportFrames)):
        if i%50 == 0:
            pma.arrays.ColumnVector(frame[:, -1]).quiver3d(origin=center)

    plt.show()

    # %% [markdown]
    # ## Scaling the OCT Data
    # %% [markdown]
    # To generate our surface we need to know the spacing between each frame and the total pixels per mm per image. This is extracted externally

    # %%
    mm_per_pixel = 0.009356
    mm_per_frame = 0.2

    # %% [markdown]
    # We first need to scale our oct data. The ivoct.Folder object has a convenience function which performs the scaling for us and provides us with the data necessary for reconstruction

    # %%
    contours, landmark, frame_id, image_files, landmark_path = folder_oct.data_scaled(mm_per_pixel).values()

    # %% [markdown]
    # # Positioning the contours
    # %% [markdown]
    # Since we are translating the contours from their centroid, to approximate the location of our artery we shall need to know where our landmark is located. We have specified the landmark as the location where the bifurcation centerline is passing through and is shown as a blue spot along the OCT image. We can do so by approximating the point perpendicular to the main centerline which lies on the bifurcation centerline for the distance specified by our landmark

    # %%
    plt.figure()
    pma.parse.ivoct.Image(landmark_path).show()
    plt.show()

    # %% [markdown]
    # The vector which passes from the contour centroid to the landmark is given by landmark. We can obtain this distance from the bar property

    # %%
    print('the landmark vector:\n', landmark)
    print(' the length of the landmark vector:', landmark.bar)

    # %% [markdown]
    # Every curve has a method which calculates the point pairs at a specified distance between another curves. Bellow we show the output as the dictionary containing the point on the main centerline, the bifurcation centerline, the error and the vector fromt he main to bifur centerlines

    # %%
    perpendicularPointDict = centerline_main.findPointPairsAtPerpendicularDistance(centerline_bifur, distance=landmark.bar, resolution=0.0001)
    print("the data required:\n", perpendicularPointDict)


    # %%
    pt_main, pt_bifur, error, vector = perpendicularPointDict.values()


    # %%
    plt.figure_3d()
    centerline_main.plot3d('b')
    centerline_bifur.plot3d('r')
    vector.quiver3d(origin=pt_main)
    pt_main.scatter3d(color='green')
    pt_bifur.scatter3d(color='red')
    plt.equal_aspect_3d_centered(pt_main)
    plt.show()

    # %% [markdown]
    # Originally our transport frames are not oriented along the centerline. But since we now have an approximation to of the orientation of our frames we can now orient our transport frames.

    # %%
    orientedTransportFrames, origin_id = centerline_main.oriented_transport_frames(
        pt_main, vector
    )
    mainTransportFrames = centerline_main.transport_frames()
    plt.figure_3d()
    centerline_main.plot3d('g')
    centerline_bifur.plot3d('r')

    # the now oriented transport frames
    pma.arrays.Basis(orientedTransportFrames[origin_id]).quiver3d(
        origin=centerline_main[:, origin_id], color='orange'
    )

    # the now original transport frames
    pma.arrays.Basis(mainTransportFrames[origin_id]).quiver3d(
        origin=centerline_main[:, origin_id], color='green'
    )
    vector.quiver3d(
        origin=centerline_main[:, origin_id], color='blue'
    )

    contour = contours[frame_id]
    contour = mainTransportFrames[origin_id] @ (contour - contour.centroid) + centerline_main[:, origin_id, None]

    contour.plot3d()

    plt.equal_aspect_3d_centered(pt_main)
    plt.show()

    # %% [markdown]
    # However this is not yet enough to orient our contours. We still need to ensure that the spacing between the frames is correct. To do so we estimate the fraction along the main centerline our landmark is located

    # %%
    s_location_landmark = centerline_main.s_frac[origin_id]
    print(s_location_landmark)

    # %% [markdown]
    # From here we can now approximate the fraction along the artery where the frames are located

    # %%
    frac_per_frame = mm_per_frame/centerline_main.s_tot
    print(frac_per_frame)

    # %% [markdown]
    # Thus we can figure out the required fractions to interpolate our centerline

    # %%
    plt.figure_3d()
    # calculate the spacing distal to the landmark
    distal_half = pma.utils.gap_space(s_location_landmark, 0, frac_per_frame)
    # calculate the spacing proximal to the landmark
    proximal_half = pma.utils.gap_space(s_location_landmark, 1, frac_per_frame)[:-1]

    #for visualiztion purposes
    main_centerlin_distal = pma.arrays.Curve(centerline_main(distal_half))
    main_centerlin_proximal = pma.arrays.Curve(centerline_main(proximal_half))

    centerline_main.plot3d('g')
    centerline_bifur.plot3d('r')

    main_centerlin_distal.plot3d('r--')
    main_centerlin_proximal.plot3d('b--')
    centerline_main[:, origin_id].scatter3d()
    plt.equal_aspect_3d_centered(pt_main)
    plt.show()

    # %% [markdown]
    # We can now calculate the required arc length fraction to obtain the required centerline

    # %%
    s_req = np.concatenate(
            [distal_half, proximal_half[1:]]
    )
    s_req.sort()
    interpolated_centerline = centerline_main(s_req)

    interpolated_landmark = len(distal_half)

    # %% [markdown]
    # The portion of the centerline used can now be calculated

    # %%
    centerline_start = interpolated_landmark-frame_id
    centerline_end = centerline_start + len(contours)
    print(centerline_start)
    print(centerline_end)
    # we should assert that the centerline start is greater than 0
    assert centerline_start > -1
    # we should assert that the amount of frames from the landmark is less than the interpolated centerline
    assert centerline_end < interpolated_centerline.shape[-1]


    # %%
    transportFrames, origin_id = interpolated_centerline.oriented_transport_frames(interpolated_centerline[:, interpolated_landmark, None], vector)
    translated_contours = []


    for j, i in enumerate(range(centerline_start, centerline_end)):
        contour = contours[j]
        contour = pma.math.make_3d(contour)
        window_size = pma.utils.make_odd(
            contour.shape[-1]//100)
        contour = pma.arrays.Contour(contour).filter(window_size, 3)
        contour = contour(np.linspace(0, 1, 100))
        contour = contour - contour.centroid
        origin = interpolated_centerline[:, i].make_column()
        basis = transportFrames[i]
        contour =  (basis @ contour) + origin
        translated_contours.append(contour)

    surface = pma.arrays.structured.CylindricalSurface.from_contours(translated_contours)
    surface.interpolate_long(300)
    surface = surface.filter(window_size=15)
    surface = surface.interpolate_contours(100)
    plt.figure_3d()
    surface.plot3d()
    plt.equal_aspect_3d()
    plt.show()


    %% [markdown]
    # High Level

    # %%
    import pyvista as pv
    path = pt.Path(cwd/r'../../Datasets/test_1')
    construct_vessel = pma.construct.ivoct.VesselSurface(path)

    surface = construct_vessel.construct(
        mm_per_frame=mm_per_frame,
        mm_per_pixel=mm_per_pixel,
        processors=4,
        centerline_type='A',
        surface_filter=25,
        interpolate_contours=360,
        centerlineResolution=0.001,
    )
    p = pv.BackgroundPlotter()
    mesh = surface.to_vtk()
    p.add_mesh(mesh)
    p.show()


    # %%
    normals, psurf = surface.calculate_normals(return_psurf=True)


    # %%
    psurf.check_all_normals()


    # %%



