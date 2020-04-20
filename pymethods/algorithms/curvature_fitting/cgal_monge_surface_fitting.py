from CGALMethods import SurfaceMesh

def monge_surface_mesh_fitting(surface_mesh, *args, d_fitting=4, d_monge=4, knn=300, internal=True):
    # kwargs = d_fitting=4, d_monge=4, knn=300, internal=True
    assert isinstance(surface_mesh, SurfaceMesh)
    surface_mesh.calculate_curvature(
        *args, d_fitting=d_fitting, d_monge=d_monge, knn=knn, internal=internal
    )
    maximum_curvature = surface_mesh.get_property("v:maximum_curvature")
    minimum_curvature = surface_mesh.get_property("v:minimum_curvature")
    return maximum_curvature, minimum_curvature


