import numpy as np
import numpy.typing as npt
import typing as tp

import shoeboxpy.utils as utils
from shoeboxpy.utils import skew
import shoeboxpy.animate


class Shoebox:
    r"""
    6-DOF rectangular "shoebox" vessel with:
      - Rigid-body mass & inertia (diagonal) from geometry (L, B, T).
      - Added mass (diagonal) from user-chosen dimensionless factors.
      - Linear damping (diagonal).
      - Simple linear restoring in roll & pitch for small angles (metacentric method).
      - **Coriolis & centripetal** effects from both rigid-body and added mass.

    States:

    .. math::
        \eta = [x, y, z, \phi, \theta, \psi]
        \nu = [u, v, w, p, q, r]

    The dynamics are:

    .. math::
        \dot{\eta} = J(\eta)\nu
    .. math::
        (M_{RB} + M_A)\dot{\nu} + (C_{RB}(\nu) + C_A(\nu))\nu + D\nu =
        \tau + \tau_{\mathrm{ext}} + g_{\mathrm{restoring}}(\eta).


    :param L: Length of the shoebox (m)
    :param B: Width of the shoebox (m)
    :param T: Height of the shoebox (m)
    :param rho: Density of the fluid :math:`(kg/m^3)`
    :param alpha_*, beta_*: Added mass & damping coefficients (dimensionless)
    :param GM_phi, GM_theta: Metacentric heights for roll & pitch
    :param g: Gravitational acceleration :math:`(m/s^2)`
    :param eta0: Initial :math:`[x, y, z, \phi, \theta, \psi]`
    :param nu0: Initial :math:`[u, v, w, p, q, r]`
    """

    def __init__(
        self,
        L: float,
        B: float,
        T: float,
        rho: float = 1000.0,
        # Added mass coefficients
        alpha_u: float = 0.1,
        alpha_v: float = 0.2,
        alpha_w: float = 1.0,
        alpha_p: float = 0.1,
        alpha_q: float = 0.1,
        alpha_r: float = 0.1,
        # Damping factors
        beta_u: float = 0.25,
        beta_v: float = 0.25,
        beta_w: float = 0.25,
        beta_p: float = 0.25,
        beta_q: float = 0.25,
        beta_r: float = 0.25,
        # Restoring parameters
        GM_phi: float = 0.0,  # metacentric height in roll
        GM_theta: float = 0.0,  # metacentric height in pitch
        g: float = 9.81,  # gravitational acceleration
        # Initial states
        eta0: npt.NDArray[np.float64] = np.zeros(6),
        nu0: npt.NDArray[np.float64] = np.zeros(6),
    ):
        r"""
        Initialize the shoebox model.

        :param L: Length of the shoebox (m)
        :param B: Width of the shoebox (m)
        :param T: Height of the shoebox (m)
        :param rho: Density of the fluid :math:`(kg/m^3)`
        :param alpha_*, beta_*: Added mass & damping coefficients (dimensionless)
        :param GM_phi, GM_theta: Metacentric heights for roll & pitch
        :param g: Gravitational acceleration :math:`(m/s^2)`
        :param eta0: Initial :math:`[x, y, z, \phi, \theta, \psi]`
        :param nu0: Initial :math:`[u, v, w, p, q, r]`
        :return: None
        """
        # 1) Rigid-body mass from volume (the code uses full L*B*T)
        self.m = rho * L * B * T

        # 2) Moments of inertia (uniform box, diagonal)
        Ix = (1.0 / 12.0) * self.m * (B**2 + T**2)
        Iy = (1.0 / 12.0) * self.m * (L**2 + T**2)
        Iz = (1.0 / 12.0) * self.m * (L**2 + B**2)

        self.MRB = np.diag([self.m, self.m, self.m, Ix, Iy, Iz])

        # 3) Added mass (diagonal)
        self.MA = np.diag(
            [
                alpha_u * self.m,
                alpha_v * self.m,
                alpha_w * self.m,
                alpha_p * Ix,
                alpha_q * Iy,
                alpha_r * Iz,
            ]
        )
        self.M_eff = self.MRB + self.MA

        # 4) Linear damping (diagonal)
        self.D = np.diag(
            [
                beta_u * self.m,
                beta_v * self.m,
                beta_w * self.m,
                beta_p * Ix,
                beta_q * Iy,
                beta_r * Iz,
            ]
        )

        self.invM_eff = np.linalg.inv(self.M_eff)

        # 5) Restoring in roll & pitch
        self.GM_phi = GM_phi
        self.GM_theta = GM_theta
        self.g = g
        # Hydrostatic stiffness for vertical buoyancy restoring: rho*g*L*B
        self.L = L
        self.B = B
        self.C_h = rho * g * L * B

        # Store states
        self.eta = eta0.astype(float)
        self.nu = nu0.astype(float)

        # Initialize reusable buffers to cut per-step allocations
        self._init_buffers()

    def _init_buffers(self) -> None:
        """Allocate persistent numpy arrays for RK4 and dynamics computations."""
        self._k_eta = np.zeros((4, 6), dtype=float)
        self._k_nu = np.zeros((4, 6), dtype=float)
        self._eta_tmp = np.zeros(6, dtype=float)
        self._nu_tmp = np.zeros(6, dtype=float)
        self._zeros6 = np.zeros(6, dtype=float)
        # Buffers for Coriolis, added mass, rhs, temp vectors
        self._C_RB = np.zeros((6, 6), dtype=float)
        self._C_A = np.zeros((6, 6), dtype=float)
        self._tmp6 = np.zeros(6, dtype=float)  # generic scratch
        self._g_rest = np.zeros(6, dtype=float)
        self._rhs = np.zeros(6, dtype=float)

    def J(self, eta):
        r"""
        Computes the 6x6 transformation matrix `J` that maps body velocities
        to the inertial frame velocities :math:`[\dot{x}, \dot{y}, \dot{y}, \dot{\phi}, \dot{\theta}, \dot{\psi}]`.
        """
        phi = eta[3]
        theta = eta[4]
        psi = eta[5]

        cphi = np.cos(phi)
        sphi = np.sin(phi)
        cth = np.cos(theta)
        sth = np.sin(theta)
        cpsi = np.cos(psi)
        spsi = np.sin(psi)

        # Rotation for linear part (body->inertial)
        R11 = cth * cpsi
        R12 = sphi * sth * cpsi - cphi * spsi
        R13 = cphi * sth * cpsi + sphi * spsi

        R21 = cth * spsi
        R22 = sphi * sth * spsi + cphi * cpsi
        R23 = cphi * sth * spsi - sphi * cpsi

        R31 = -sth
        R32 = sphi * cth
        R33 = cphi * cth

        R_lin = np.array([[R11, R12, R13], [R21, R22, R23], [R31, R32, R33]])

        eps = 1e-9
        tth = sth / max(cth, eps)
        scth = 1.0 / max(cth, eps)

        T_ang = np.array(
            [
                [1.0, sphi * tth, cphi * tth],
                [0.0, cphi, -sphi],
                [0.0, sphi * scth, cphi * scth],
            ]
        )

        return np.block([[R_lin, np.zeros((3, 3))], [np.zeros((3, 3)), T_ang]])

    def C_RB(self, nu: np.ndarray) -> np.ndarray:
        r"""
        Rigid-body Coriolis/centripetal matrix for diagonal :math:`M_{RB}`.
        (assuming CG at origin, no product of inertia).
        """
        u, v, w, p, q, r = nu

        m = self.m
        Ix = self.MRB[3, 3]
        Iy = self.MRB[4, 4]
        Iz = self.MRB[5, 5]

        # Build the 6x6 in block form:
        # top-left = 0
        # top-right = -m * S([p,q,r])
        # bottom-left = -m * S([u,v,w])
        # bottom-right = - S(I * [p,q,r])
        C = np.zeros((6, 6))

        v_b = np.array([u, v, w])
        w_b = np.array([p, q, r])
        Iw_b = np.array([Ix * p, Iy * q, Iz * r])  # diagonal inertia times w

        C[:3, :3] = 0.0
        C[:3, 3:] = -m * skew(w_b)
        C[3:, :3] = -skew(m * v_b)
        C[3:, 3:] = -skew(Iw_b)

        return C

    def C_A(self, nu: np.ndarray) -> np.ndarray:
        r"""
        Added-mass Coriolis/centripetal matrix for diagonal :math:`M_A`.
        """
        u, v, w, p, q, r = nu

        Xudot = self.MA[0, 0]
        Yvdot = self.MA[1, 1]
        Zwdot = self.MA[2, 2]
        Kpdot = self.MA[3, 3]
        Mqdot = self.MA[4, 4]
        Nrdot = self.MA[5, 5]

        # Similar block structure, using "added mass" equivalents
        C = np.zeros((6, 6))

        v_b = np.array([u, v, w])
        w_b = np.array([p, q, r])

        # linear part: M_A,lin * v_b
        # rotational part: M_A,rot * w_b
        Mlin_v = np.array([Xudot * u, Yvdot * v, Zwdot * w])
        Mrot_w = np.array([Kpdot * p, Mqdot * q, Nrdot * r])

        # top-left = 0
        # top-right = - skew( M_A,lin v_b )
        # bottom-left = - skew( M_A,lin v_b )
        # bottom-right = - skew( M_A,rot w_b )
        C[:3, :3] = 0.0
        C[:3, 3:] = -skew(Mlin_v)
        C[3:, :3] = -skew(Mlin_v)
        C[3:, 3:] = -skew(Mrot_w)

        return C

    def restoring_forces(self, eta: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Compute hydrostatic restoring forces for vertical (z), roll, and pitch."""
        # unpack state: x, y, z, phi, theta, psi
        _, _, z, phi, theta, _ = eta
        # vertical buoyancy restoring: hydrostatic stiffness * displacement
        F_z = - self.C_h * z
        # roll & pitch restoring moments
        K_rest = - self.m * self.g * self.GM_phi * phi
        M_rest = - self.m * self.g * self.GM_theta * theta
        return np.array([0.0, 0.0, F_z, K_rest, M_rest, 0.0])

    def dynamics(
        self,
        eta: npt.NDArray[np.float64],
        nu: npt.NDArray[np.float64],
        tau: npt.NDArray[np.float64],
        tau_ext: npt.NDArray[np.float64],
    ) -> tp.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Public API returning new arrays (kept for backward compatibility)."""
        eta_dot = np.empty(6, dtype=float)
        nu_dot = np.empty(6, dtype=float)
        self._dynamics_into(eta, nu, tau, tau_ext, eta_dot, nu_dot)
        return eta_dot, nu_dot

    def _dynamics_into(
        self,
        eta: npt.NDArray[np.float64],
        nu: npt.NDArray[np.float64],
        tau: npt.NDArray[np.float64],
        tau_ext: npt.NDArray[np.float64],
        eta_dot_out: npt.NDArray[np.float64],
        nu_dot_out: npt.NDArray[np.float64],
    ) -> None:
        """Compute dynamics in-place without allocating temporary large arrays."""
        if tau_ext is None:
            tau_ext = self._zeros6

        # Unpack
        x, y, z, phi, theta, psi = eta
        u, v, w, p, q, r = nu

        # Precompute trig
        cphi = np.cos(phi); sphi = np.sin(phi)
        cth = np.cos(theta); sth = np.sin(theta)
        cpsi = np.cos(psi); spsi = np.sin(psi)

        eps = 1e-9
        tth = sth / max(cth, eps)
        inv_cth = 1.0 / max(cth, eps)

        # Kinematics: translational part R_lin * [u,v,w]
        # Rows of R_lin
        R11 = cth * cpsi
        R12 = sphi * sth * cpsi - cphi * spsi
        R13 = cphi * sth * cpsi + sphi * spsi
        R21 = cth * spsi
        R22 = sphi * sth * spsi + cphi * cpsi
        R23 = cphi * sth * spsi - sphi * cpsi
        R31 = -sth
        R32 = sphi * cth
        R33 = cphi * cth
        eta_dot_out[0] = R11 * u + R12 * v + R13 * w
        eta_dot_out[1] = R21 * u + R22 * v + R23 * w
        eta_dot_out[2] = R31 * u + R32 * v + R33 * w

        # Angular mapping T_ang * [p,q,r]
        eta_dot_out[3] = p + sphi * tth * q + cphi * tth * r
        eta_dot_out[4] = cphi * q - sphi * r
        eta_dot_out[5] = sphi * inv_cth * q + cphi * inv_cth * r

        # Coriolis and added mass matrices applied to nu
        C_RB = self._C_RB; C_A = self._C_A
        C_RB.fill(0.0); C_A.fill(0.0)

        # Helper inline skew fill
        def _fill_skew(a, out):
            ax, ay, az = a
            out[0,0]=0.0; out[0,1]=-az; out[0,2]=ay
            out[1,0]=az; out[1,1]=0.0; out[1,2]=-ax
            out[2,0]=-ay; out[2,1]=ax; out[2,2]=0.0

        m = self.m
        Ix = self.MRB[3,3]; Iy = self.MRB[4,4]; Iz = self.MRB[5,5]

        v_b = (u, v, w)
        w_b = (p, q, r)
        # top-right = -m * skew(w_b)
        _fill_skew(w_b, C_RB[:3,3:])
        C_RB[:3,3:] *= -m
        # bottom-left = -skew(m*v_b)
        mv_b = (m*u, m*v, m*w)
        _fill_skew(mv_b, C_RB[3:,:3])
        C_RB[3:,:3] *= -1.0
        # bottom-right = -skew(I*w_b)
        Iw = (Ix*p, Iy*q, Iz*r)
        _fill_skew(Iw, C_RB[3:,3:])
        C_RB[3:,3:] *= -1.0

        # Added mass Coriolis
        Xudot = self.MA[0,0]; Yvdot = self.MA[1,1]; Zwdot = self.MA[2,2]
        Kpdot = self.MA[3,3]; Mqdot = self.MA[4,4]; Nrdot = self.MA[5,5]
        Mlin_v = (Xudot*u, Yvdot*v, Zwdot*w)
        Mrot_w = (Kpdot*p, Mqdot*q, Nrdot*r)
        _fill_skew(Mlin_v, C_A[:3,3:]); C_A[:3,3:] *= -1.0
        _fill_skew(Mlin_v, C_A[3:,:3]); C_A[3:,:3] *= -1.0
        _fill_skew(Mrot_w, C_A[3:,3:]); C_A[3:,3:] *= -1.0

        # Compute C_total @ nu using buffers
        tmp = self._tmp6
        tmp[:] = C_RB @ nu
        tmp += C_A @ nu

        # Restoring forces (write into _g_rest)
        g_rest = self._g_rest
        g_rest.fill(0.0)
        # vertical
        g_rest[2] = - self.C_h * z
        # roll & pitch
        g_rest[3] = - self.m * self.g * self.GM_phi * phi
        g_rest[4] = - self.m * self.g * self.GM_theta * theta

        # rhs = tau + tau_ext + g_rest - D@nu - C_total@nu
        rhs = self._rhs
        # D is diagonal
        D = self.D
        rhs[:] = tau + tau_ext + g_rest - tmp - np.array([
            D[0,0]*u, D[1,1]*v, D[2,2]*w, D[3,3]*p, D[4,4]*q, D[5,5]*r
        ])

        # nu_dot = invM_eff @ rhs
        invM = self.invM_eff
        # manual matvec for slight speed (small size)
        for i in range(6):
            nu_dot_out[i] = invM[i,0]*rhs[0] + invM[i,1]*rhs[1] + invM[i,2]*rhs[2] + \
                             invM[i,3]*rhs[3] + invM[i,4]*rhs[4] + invM[i,5]*rhs[5]

    def step(self, tau=None, tau_ext=None, dt=0.01):
        r"""Advance (eta, nu) one step using RK4 with preallocated buffers."""
        if tau is None:
            tau = self._zeros6.copy()
        if tau_ext is None:
            tau_ext = self._zeros6

        eta0 = self.eta
        nu0 = self.nu
        k_eta = self._k_eta
        k_nu = self._k_nu
        eta_tmp = self._eta_tmp
        nu_tmp = self._nu_tmp

        # k1
        self._dynamics_into(eta0, nu0, tau, tau_ext, k_eta[0], k_nu[0])
        # k2
        eta_tmp[:] = eta0 + 0.5 * dt * k_eta[0]
        nu_tmp[:] = nu0 + 0.5 * dt * k_nu[0]
        self._dynamics_into(eta_tmp, nu_tmp, tau, tau_ext, k_eta[1], k_nu[1])
        # k3
        eta_tmp[:] = eta0 + 0.5 * dt * k_eta[1]
        nu_tmp[:] = nu0 + 0.5 * dt * k_nu[1]
        self._dynamics_into(eta_tmp, nu_tmp, tau, tau_ext, k_eta[2], k_nu[2])
        # k4
        eta_tmp[:] = eta0 + dt * k_eta[2]
        nu_tmp[:] = nu0 + dt * k_nu[2]
        self._dynamics_into(eta_tmp, nu_tmp, tau, tau_ext, k_eta[3], k_nu[3])

        eta0 += (dt / 6.0) * (k_eta[0] + 2*k_eta[1] + 2*k_eta[2] + k_eta[3])
        nu0 += (dt / 6.0) * (k_nu[0] + 2*k_nu[1] + 2*k_nu[2] + k_nu[3])

    def get_states(self):
        return self.eta.copy(), self.nu.copy()


if __name__ == "__main__":
    # Example usage
    dt = 0.01
    T_total = 300.0
    shoebox = Shoebox(
        L=1.0,
        B=0.3,
        T=0.03,
        eta0=np.array([0.0, 0.0, 0.0, 0.1, 0.1, 0.1]),
        nu0=np.zeros(6),
        GM_phi=0.2,
        GM_theta=0.2,
    )

    eta_history = []

    # Simulate for 10 seconds with no control input
    for t in range(int(T_total / dt)):
        shoebox.step(tau=np.array([1.0, 0.2, 0.0, 0.0, 0.0, 0.1]), dt=dt)
        eta_history.append(shoebox.eta.copy())

    eta_history = np.array(eta_history)
    shoeboxpy.animate.animate_history(eta_history, dt=dt, L=1.0, B=0.3, T=0.2)
