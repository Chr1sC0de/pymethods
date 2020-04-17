from CGALMethods import SurfaceMesh

def monge_surface_mesh_fitting(surface_mesh, *args, **kwargs):
    assert isinstance(surface_mesh, SurfaceMesh)
    surface_mesh.calculate_curvature(*args, **kwargs)
    maximum_curvature = surface_mesh.get_property("v:maximum_curvature")
    minimum_curvature = surface_mesh.get_property("v:minimum_curvature")
    return maximum_curvature, minimum_curvature


