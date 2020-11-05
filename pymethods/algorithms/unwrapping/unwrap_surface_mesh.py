import CGALMethods as CM
import pyvista as pv
import pathlib as pt
import numpy as np

try:
    from pymethods import arrays, math, pyplot
except:
    from .. import arrays, math, pyplot

def get_centerline_from_cylindrical_mesh(surface_mesh, inlet_origin=None):

    # surface mesh is the path to the surface mesh

    if inlet_origin is not None:
        unwrapped = CM.unwrap_cylindrical_surface_mesh(surface_mesh, *inlet_origin)
    else:
        unwrapped = CM.unwrap_cylindrical_surface_mesh(surface_mesh)

    gridded = CM.map_parameterized_mesh_to_grid(unwrapped)

    original_points = gridded["original_points"]

    centerline = arrays.structured.CylindricalSurface.get_centerline(original_points)

    return centerline

def unwrap_cylinder_vtk_from_centerline(centerline, pv_mesh, clip=3, points_per_contour=256):

    s = np.linspace(0, 1, len(centerline.T)+clip*2)
    centerline = centerline(s)

    tangents = math.normalize(np.gradient(centerline, axis=-1, edge_order=2))
    transport_frames = centerline.transport_frames()
    slices = []

    for i, (frame, c) in enumerate(zip(transport_frames, centerline.T)):

        t = frame[:,-1]

        # uncomment to check the clipping
        # if (any([i==clip, i>=(max(centerline.shape)-clip)])):
        #     cut = pv_mesh.slice(normal=t, origin=c)
        #     cut.plot()

        if (all([i>=clip, i<(max(centerline.shape)-clip)])):

            cut = pv_mesh.slice(normal=t, origin=c)

            connected_regions = cut.connectivity()

            unique_arrays = np.unique(connected_regions.point_arrays['RegionId'])

            if len(unique_arrays) > 1:
                min_distance = 1000000000;

                for region in unique_arrays:
                    mask = connected_regions.point_arrays['RegionId'] == region
                    points = connected_regions.points[mask]
                    distance = math.l2_norm(points.mean() -  c).squeeze()
                    if distance < min_distance:

                        min_distance = distance
                        min_id = unique_arrays
                        required_mask = mask

            else:
                min_id = unique_arrays.squeeze()
                required_mask = connected_regions.point_arrays['RegionId'] == unique_arrays

            current_slice = {}
            current_slice['points'] = connected_regions.points[required_mask]
            current_slice['point_arrays'] = {}
            for key in connected_regions.point_arrays.keys():
                if key != "RegionId":
                    current_slice["point_arrays"][key] = connected_regions.point_arrays[key][required_mask]

            contour_field = arrays.FieldContour(
                current_slice["points"].T,
                fields = dict([
                    (key, current_slice["point_arrays"][key].T)
                    for key in current_slice["point_arrays"].keys()
                ])
            )

            contour_field = contour_field.sortByBasis(frame)

            slices.append(contour_field(np.linspace(0, 1, points_per_contour)))

    # create grids out of the slices
    point_grid = np.stack(slices, axis=-1)
    field_grids = {}
    for key in slices[0].fields.keys():
        field_stack = [
            s.fields[key] for s in slices
        ]
        field_stack = np.stack(field_stack, axis=-1)
        field_grids[key] = field_stack

    # create the cylinder stack
    point_grid, field_grid = arrays.structured.CylindricalSurface.align_contour_points(
        slices, field_grids=field_grids)

    # # plot the resulting fields
    # pyplot.imshow(point_grid[0])
    # pyplot.show()
    # pyplot.imshow(point_grid[1])
    # pyplot.show()
    # pyplot.imshow(point_grid[2])
    # pyplot.show()
    # pyplot.imshow(field_grids['magWallShearStress'][0])
    # pyplot.show()

    return point_grid, field_grids


def unwrap_cylindrical_vtk_using_centerline(
        pv_mesh, inlet_origin=None,
        clip=3, points_per_contour=256,
        number_centerline_points=384
    ):

    assert isinstance(pv_mesh, (pt.Path, str))

    pv_mesh = pt.Path(pv_mesh)

    surface_mesh = CM.SurfaceMesh(pv_mesh.as_posix())
    pv_mesh = pv.read(pv_mesh.as_posix())

    if inlet_origin is not None:
        centerline = get_centerline_from_cylindrical_mesh(
            surface_mesh,
            inlet_origin=inlet_origin)
    else:
        centerline = get_centerline_from_cylindrical_mesh(surface_mesh)

    centerline = centerline(np.linspace(0, 1, number_centerline_points))

    return unwrap_cylinder_vtk_from_centerline(centerline, pv_mesh)


if __name__ == "__main__":
    vtk_path = pt.Path(r"I:\vtkData\00001\WALL\WALL_400.vtk")
    unwrapped = unwrap_cylindrical_vtk_using_centerline(vtk_path)
    pass
