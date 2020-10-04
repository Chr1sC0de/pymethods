from .chord_normal_vectors import can_lsq_fit
try:
    from .cgal_monge_surface_fitting import monge_surface_mesh_fitting
except:
    pass

__All__ = ['can_lsq_fit', 'monge_surface_mesh_fitting']