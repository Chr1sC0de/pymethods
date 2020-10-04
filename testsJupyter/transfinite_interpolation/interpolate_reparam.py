import numpy as np
import pathlib as pt
import pymethods as pma

cwd = pt.Path(__file__).parent

angio_surface = np.load(cwd/'../../Datasets/artery_structure_grid/00000.npz')

angio_surface = pma.arrays.structured.CylindricalSurface(
    angio_surface['points']
)

if False:
    interpolated_surface = angio_surface.interpolate_long(50, centerline_reparam=True)
    interpolated_surface.scatter3d()
    pma.pyplot.equal_aspect_3d()
    pma.pyplot.show()

if True:
    interpolated_surface = angio_surface(
        np.linspace(0, 1, 10),
        np.linspace(0, 1, 20)
    )
    interpolated_surface.scatter3d()
    pma.pyplot.equal_aspect_3d()

if True:
    interpolated_surface = angio_surface(
            np.linspace(0, 0.5, 10),
            np.linspace(0, 1, 20)
        )
    interpolated_surface.scatter3d(color='red')
    pma.pyplot.equal_aspect_3d()

if True:
    interpolated_surface = angio_surface(
            np.linspace(0, 0.5, 10),
            np.linspace(0, 0.5, 20)
        )
    interpolated_surface.scatter3d(color='green')
    pma.pyplot.equal_aspect_3d()

if True:
    interpolated_surface = angio_surface(
            np.linspace(0, 1, 10),
            np.linspace(0, 0.5, 20)
        )
    interpolated_surface.scatter3d(color='orange')
    pma.pyplot.equal_aspect_3d()

pma.pyplot.show()
