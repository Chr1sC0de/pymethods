import numpy as np
from numba import jit
inner = np.s_[1:-1]
ip1 = np.s_[2:]
im1 = np.s_[0:-2]


def G11(mesh, zeta, eta):
    x, y = mesh
    numerator_1 = x[inner, ip1] - x[inner, im1]
    denominator_1 = 2 * zeta
    numerator_2 = y[inner, ip1] - y[inner, im1]
    denominator_2 = 2 * zeta
    a = (numerator_1/denominator_1)**2
    b = (numerator_2/denominator_2)**2
    return a+b


def G22(mesh, zeta, eta):
    x, y = mesh
    numerator_1 = x[ip1, inner] - x[im1, inner]
    denominator_1 = 2 * eta
    numerator_2 = y[ip1, inner] - y[im1, inner]
    denominator_2 = 2 * eta
    a = (numerator_1/denominator_1)**2
    b = (numerator_2/denominator_2)**2
    return a+b


def G12(mesh, zeta, eta):
    x, y = mesh
    a = ((x[inner, ip1] - x[inner, im1])*(x[ip1, inner] - x[im1, inner]))/ \
        (2*zeta*2*eta)
    b = ((y[inner,  ip1] - y[inner, im1])*(y[ip1, inner] - y[im1, inner]))/ \
        (2*zeta*2*eta)
    return a+b


def constructCoefficients(mesh, zeta, eta):
    x, y = mesh

    g11 = G11(mesh, zeta, eta)
    g22 = G22(mesh, zeta, eta)
    g12 = G12(mesh, zeta, eta)

    deTerm = g22/(zeta*eta)
    dTerm = 0.5 * g12 * \
        (x[ip1, ip1] + x[im1, im1] - x[ip1, im1] - x[im1, ip1])
    eTerm = 0.5 * g12 * \
        (y[ip1, ip1] + y[im1, im1] - y[ip1, im1] - y[im1, ip1])

    b = 2 * (
        g11/(zeta*eta) +
        g22/(zeta*eta)
    )
    a = g11/(eta*zeta)
    return a, b, deTerm, dTerm, eTerm


def solveTDMA(phi, a, b, deTerm, dTerm):
    P = np.zeros(phi.shape[1])
    Q = np.zeros(phi.shape[1])
    bArr = np.zeros(phi.shape[1])
    for i in np.arange(1, phi.shape[1]-1):
        Q[0] = phi[0][i]
        for j in np.arange(1, phi.shape[0]-1):
            P[j] = a[j-1][i-1]
            Q[j] = deTerm[j-1][i-1] * (phi[j][i + 1] + phi[j][i - 1]) + dTerm[j-1][i-1]
            bArr[j] = b[j-1][i-1]
            term = 1.0 / (bArr[j] - P[j] * P[j - 1])
            Q[j] = (Q[j] + P[j] * Q[j - 1]) * term
            P[j] = P[j] * term
        for j in np.arange(phi.shape[-1]-2, -1, -1):
            phi[j][i] = P[j] * phi[j + 1][i] + Q[j]


def optimize(new_mesh, zeta, eta, epsilon=1e-5, max_repeats=1000, residualInit=1000):
    n_iters = 0
    residual = residualInit
    while residual > epsilon:
        old_mesh = new_mesh.copy()
        n_iters += 1
        a, b, deTerm, dTerm, eTerm = constructCoefficients(new_mesh, zeta, eta)
        solveTDMA(new_mesh[0], a, b, deTerm, dTerm)
        solveTDMA(new_mesh[1], a, b, deTerm, eTerm)
        residual = (np.abs(old_mesh-new_mesh)).mean()
        if n_iters > max_repeats:
            break
    return new_mesh


class mesh2d:

    def __init__(self, mesh2d, zeta, eta):
        mesh2d = mesh2d[0:2]
        assert mesh2d.shape[0] == 2
        self.mesh = mesh2d
        self.zeta = zeta
        self.eta = eta

    def __call__(self, epsilon=1e-5, max_repeats=1000, residualInit=1000):
        new_mesh = self.mesh.copy()

        zeta, eta = [self.zeta, self.eta]

        new_mesh = optimize(
            new_mesh, zeta, eta, epsilon=epsilon, max_repeats=max_repeats,
            residualInit=residualInit)

        return new_mesh
