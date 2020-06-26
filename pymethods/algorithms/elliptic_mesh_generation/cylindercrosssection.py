import numpy as np
try:
    from pymethods.algorithms.transfinite_interpolation import Transfinite2d
    from pymethods.algorithms import elliptic_mesh_generation as emg
    from pymethods.arrays import Contour
    from pymethods import pyplot as plt
except:
    from ..transfinite_interpolation import Transfinite2d
    from .. import elliptic_mesh_generation as emg
    from ...arrays import Contour
    from ... import pyplot as plt


class CylindricalElllipticGridSolver2d:

    def __init__(
        self, contourstack, 
        alpha=-0.1, beta=-0.1,
        stretch=False
    ):
        assert len(contourstack.shape) == 3

        self.alpha = alpha
        self.beta = beta
        self.stretch = stretch

        self.contourstack = contourstack

    def solve(self, xx, yy, **kwargs):

        n_contours = self.contourstack.shape[-1]

        solved_contours = np.zeros_like(self.contourstack)

        for contour_id in range(n_contours):

            contour = Contour(self.contourstack[:, :, contour_id], write_end=True)
            centroid = contour.centroid
            basis = contour.calc_basis()

            transfinite_interpolator = Transfinite2d(contour)

            grid, (zeta_orig, eta_orig) = transfinite_interpolator.pts_mesh_uniform(
                xx, yy, return_params=True
            )

            centered_contour = grid - centroid[:, :, None]
            flattened = np.einsum("ij, jkl -> ikl", basis.T, centered_contour)

            zeta_s = np.linspace(0, 1, xx) 
            eta_s = np.linspace(0, 1, yy)

            zeta = zeta_s[1] + zeta_s[0]
            eta = eta_s[1] + eta_s[0]
            
            if not self.stretch:
                elliptic_solver = emg.mesh2d(flattened, zeta, eta)
            else:
                elliptic_solver = emg.meshStretch2d(flattened, zeta, eta, zeta_orig, eta_orig)
            
            solved = elliptic_solver(**kwargs)

            solved = np.concatenate(
                [solved, np.zeros_like(solved[0, None])], axis=0
            )

            solved = np.einsum("ij, jkl -> ikl", basis, solved) + centroid[:, :, None]

            # for debugging
            # _, ax = plt.gcfa3d()
            # ax.plot_wireframe(*solved, color="green")
            # plt.show()

            solved_contours[:, :, contour_id]
        
        return solved_contours
        

if __name__ == "__main__":

    import pathlib as pt
    import time 

    # this is slow as heck in python

    cwd = pt.Path(__file__).parent

    dataset_folder = cwd/'../../../Datasets/artery_structure_grid'

    assert dataset_folder.exists()

    data_file = dataset_folder/'00000.npz'
    data = np.load(data_file)
    oct_pts = data["points"]

    solver = CylindricalElllipticGridSolver2d(oct_pts)

    start = time.time()
    mesh = solver.solve(30, 30)
    end = time.time()

    print("the total time taken:", start-end)
