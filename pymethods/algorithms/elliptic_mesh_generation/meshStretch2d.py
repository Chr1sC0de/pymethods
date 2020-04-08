import numpy as np
inner = np.s_[1:-1]
ip1 = np.s_[2:]
im1 = np.s_[0:-2]


def f1Prime(alpha, zeta):

    return alpha * np.exp(alpha * zeta) / (np.exp(alpha) - 1)


def f1PrimePrime(alpha, zeta):

    return (alpha**2) * np.exp(alpha * zeta) / (np.exp(alpha)-1)


def f2Prime(beta, eta):
    return beta * np.exp(beta * eta) / (np.exp(beta)-1)


def f2PrimePrime(beta, eta):
    return (beta**2) * np.exp(beta * eta) / (np.exp(beta)-1)


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


def constructCoefficients(
            mesh, zeta_delta, eta_delta, zeta_params, eta_params, alpha, beta
        ):
    x, y = mesh

    height, length = x.shape

    g11 = G11(mesh, zeta_delta, eta_delta)
    g22 = G22(mesh, zeta_delta, eta_delta)

    f2_double_over_single_prime = (
        f2PrimePrime(beta, eta_params[inner, inner])/f2Prime(beta, eta_params[inner, inner])
    )

    f1_double_over_single_prime = (
        f1PrimePrime(alpha, zeta_params[inner, inner])/f1Prime(alpha, zeta_params[inner, inner])
    )

    b = 2 * (g11/(eta_delta**2) + g22/(zeta_delta**2))

    a = f2_double_over_single_prime * g11 / (2*eta_delta) + g11/(eta_delta ** 2)

    c = - f2_double_over_single_prime * g11 / (2*eta_delta) + g11/(eta_delta**2)

    dTerm = (
        g22 / zeta_delta * (
            x[inner, im1]/zeta_delta +
            f1_double_over_single_prime * x[inner, im1]/2 +
            x[inner, ip1]/zeta_delta -
            f1_double_over_single_prime * x[inner, ip1]/2
        )
    )

    eTerm = (
        g22 / zeta_delta * (
            y[inner, im1]/zeta_delta +
            f1_double_over_single_prime * y[inner, im1] / 2 +
            y[inner, ip1]/zeta_delta -
            f1_double_over_single_prime * y[inner, ip1]/2
        )
    )

    return a, b, c, dTerm, eTerm


def solveTDMA(phi, a, b, c, dTerm):
    P = np.zeros(phi.shape[1])
    Q = np.zeros(phi.shape[1])
    bArr = np.zeros(phi.shape[1])
    aArr = np.zeros(phi.shape[1])
    for i in np.arange(1, phi.shape[1]-1):
        Q[0] = phi[0][i]
        for j in np.arange(1, phi.shape[0]-1):
            P[j] = c[j-1][i-1]
            Q[j] = dTerm[j-1][i-1]
            bArr[j] = b[j-1][i-1]
            aArr[j] = a[j-1][i-1]
            term = 1.0 / (bArr[j] - aArr[j] * P[j - 1])
            Q[j] = (Q[j] + aArr[j] * Q[j - 1]) * term
            P[j] = P[j] * term
        for j in np.arange(phi.shape[-1]-2, -1, -1):
            phi[j][i] = P[j] * phi[j + 1][i] + Q[j]


def optimize(new_mesh, zeta_delta, eta_delta, zeta_params, eta_params,
             alpha=0.01, beta=0.01, epsilon=1e-5, max_repeats=1000, residualInit=1000):
    n_iters = 0
    residual = residualInit
    while residual > epsilon:
        old_mesh = new_mesh.copy()
        n_iters += 1
        a, b, c, dTerm, eTerm = constructCoefficients(
            new_mesh, zeta_delta, eta_delta, zeta_params, eta_params, alpha, beta
        )
        solveTDMA(new_mesh[0], a, b, c, dTerm)
        solveTDMA(new_mesh[1], a, b, c, eTerm)
        residual = (np.abs(old_mesh-new_mesh)).mean()
        if n_iters > max_repeats:
            break
    return new_mesh


class meshStretch2d:

    def __init__(self, mesh2d, zeta_delta, eta_delta, zeta_orig, eta_orig):
        mesh2d = mesh2d[0:2]
        assert mesh2d.shape[0] == 2
        self.mesh = mesh2d
        self.zeta_delta = zeta_delta
        self.eta_delta = eta_delta
        self.zeta_orig = zeta_orig
        self.eta_orig = eta_orig

    def __call__(self, **kwargs):
        new_mesh = self.mesh.copy()

        zeta_delta, eta_delta, zeta_orig, eta_orig = [
            self.zeta_delta, self.eta_delta, self.zeta_orig, self.eta_orig]

        new_mesh = optimize(
            new_mesh, zeta_delta, eta_delta,
            zeta_orig, eta_orig, **kwargs)

        return new_mesh
