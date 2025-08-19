__all__ = [
    'DisorderFullProtomon',
]

# code from Xinyuan

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.special import kn

import scqubits.core.constants as constants
import scqubits.core.discretization as discretization
import scqubits.core.oscillator as osc
import scqubits.core.operators as op
import scqubits.core.qubit_base as base
import scqubits.core.storage as storage
import scqubits.io_utils.fileio_serializers as serializers
import scqubits.utils.plotting as plot
import scqubits.utils.spectrum_utils as spec_utils
import scqubits.utils.spectrum_utils as matele_utils


# — Inductively-shunted Rhombus circuit ————————————————————————
class DisorderFullProtomon(base.QubitBaseClass, serializers.Serializable):
    r"""
    Xianyuan's code
    inductively-shunted Rhombus qubit, with the harmonic mode in the ground state

    Parameters
    ----------
    EJ: float
        Josephson energy
    EC: float
        junction charging energy
    ECP: float
        parasitic capacitance energy
    EL: float
        inductive energy
    ELA: float
        additional inductive energy
    flux_c: float
        common part of the external flux, e.g., 1 corresponds to one flux quantum
    flux_d: float
        differential part of the external flux, e.g., 1 corresponds to one flux quantum
    kbt: float
        photon temperature
    """

    def __init__(self, EJ, EC, ECP, EL, ELA, dC, dL, dJ, flux_c, flux_d, kbt):
        self.EJ = EJ
        self.EC = EC
        self.ECP = ECP
        self.EL = EL
        self.ELA = ELA
        self.dC = dC
        self.dL = dL
        self.dJ = dJ
        self.flux_c = flux_c
        self.flux_d = flux_d
        self.kbt = kbt * 1e-3 * 1.38e-23 / 6.63e-34 / 1e9  # input temperature unit mK
        self.phi_grid = discretization.Grid1d(-4 * np.pi, 4 * np.pi, 90)
        self.theta_grid = discretization.Grid1d(-4 * np.pi, 4 * np.pi, 100)
        self.zeta_grid = discretization.Grid1d(-4 * np.pi, 4 * np.pi, 110)
        self.zeta_cut = 10
        self.truncated_dim = 20
        self.ph = 0  # placeholder
        self._sys_type = type(self).__name__
        self._evec_dtype = np.float_

    @staticmethod
    def default_params():
        return {
            "EJ": 15.0,
            "EC": 3.5,
            "EL": 0.32,
            "ELA": 0.32,
            "flux_c": 0.5,
            "flux_d": 0.0,
        }

    @staticmethod
    def nonfit_params():
        return ["flux_c", "flux_d"]

    def dim_phi(self):
        """
        Returns
        -------
        int
            Returns the Hilbert space dimension of :math:`phi' degree of freedom."""
        return self.phi_grid.pt_count

    def dim_theta(self):
        """
        Returns
        -------
        int
            Returns the Hilbert space dimension of :math:`theta' degree of freedom."""
        return self.theta_grid.pt_count

    def dim_zeta(self):
        """
        Returns
        -------
        int
            Returns the Hilbert space dimension of :math:`theta' degree of freedom."""
        return self.zeta_cut

    def zeta_plasma(self):
        return np.sqrt(
            4
            * 4
            * self.ECP
            * (
                0.5 * self.ELA
                + 0.5 * self.EL / (1 - self.dL)
                + 0.5 * self.EL / (1 + self.dL)
            )
        )

    def zeta_osc(self):
        """
        Returns
        -------
        float
            Returns the oscillator strength of :math:`zeta' degree of freedom."""
        return (
            4
            * self.ECP
            / (
                0.5 * self.ELA
                + 0.5 * self.EL / (1 - self.dL)
                + 0.5 * self.EL / (1 + self.dL)
            )
        ) ** 0.25

    def hilbertdim(self):
        """
        Returns
        -------
        int
            Returns the total Hilbert space dimension."""
        return self.dim_phi() * self.dim_zeta() * self.dim_theta()

    def _zeta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`zeta' operator in the LC harmonic oscillator basis
        """
        dimension = self.dim_zeta()
        return (
            (op.creation_sparse(dimension) + op.annihilation_sparse(dimension))
            * self.zeta_osc()
            / np.sqrt(2)
        )

    def zeta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`phi' operator in total Hilbert space
        """
        return self._kron3(
            self._identity_phi(), self._zeta_operator(), self._identity_theta()
        )

    def _n_zeta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`n_\phi = - i d/d\\phi` operator
        """
        dimension = self.dim_zeta()
        return (
            1j
            * (op.creation_sparse(dimension) - op.annihilation_sparse(dimension))
            / (self.zeta_osc() * np.sqrt(2))
        )

    def n_zeta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`n_phi' operator in total Hilbert space
        """
        return self._kron3(
            self._identity_phi(), self._n_zeta_operator(), self._identity_theta()
        )

    def _phi_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`\phi` operator in the discretized basis
        """
        return sparse.dia_matrix(
            (self.phi_grid.make_linspace(), [0]), shape=(self.dim_phi(), self.dim_phi())
        ).tocsc()

    def phi_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`phi' operator in total Hilbert space
        """
        return self._kron3(
            self._phi_operator(), self._identity_zeta(), self._identity_theta()
        )

    def _n_phi_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`n_\phi = - i d/d\\phi` operator
        """
        return self.phi_grid.first_derivative_matrix(prefactor=-1j)

    def n_phi_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`n_phi' operator in total Hilbert space
        """
        return self._kron3(
            self._n_phi_operator(), self._identity_zeta(), self._identity_theta()
        )

    def _cos_phi_div_operator(self, div, off=0.0):
        """
        Returns
        -------
        ndarray
            Returns the :math:`\\cos (\\phi+off)/div` operator
        """
        cos_phi_div_vals = np.cos((self.phi_grid.make_linspace() + off) / div)
        return sparse.dia_matrix(
            (cos_phi_div_vals, [0]), shape=(self.dim_phi(), self.dim_phi())
        ).tocsc()

    def _sin_phi_div_operator(self, div, off=0.0):
        """
        Returns
        -------
        ndarray
            Returns the :math:`\\sin (\\phi+off)/div` operator
        """
        sin_phi_div_vals = np.sin((self.phi_grid.make_linspace() + off) / div)
        return sparse.dia_matrix(
            (sin_phi_div_vals, [0]), shape=(self.dim_phi(), self.dim_phi())
        ).tocsc()

    def _theta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`theta' operator in total Hilbert space
        """
        return sparse.dia_matrix(
            (self.theta_grid.make_linspace(), [0]),
            shape=(self.dim_theta(), self.dim_theta()),
        ).tocsc()

    def theta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`theta' operator in total Hilbert space
        """
        return self._kron3(
            self._identity_phi(), self._identity_zeta(), self._theta_operator()
        )

    def _n_theta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns the :math:`n_\theta = - i d/d\\theta` operator
        """
        return self.theta_grid.first_derivative_matrix(prefactor=-1j)

    def n_theta_operator(self):
        """
        Returns
        -------
        ndarray
            Returns charge operator :math:`\\n_theta` in the total Hilbert space
        """
        return self._kron3(
            self._identity_phi(), self._identity_zeta(), self._n_theta_operator()
        )

    def _cos_theta_div_operator(self, div, off=0.0):
        """
        Returns
        -------
        ndarray
            Returns the :math:`\\cos (\\theta+off)/div` operator
        """
        cos_theta_div_vals = np.cos((self.theta_grid.make_linspace() + off) / div)
        return sparse.dia_matrix(
            (cos_theta_div_vals, [0]), shape=(self.dim_theta(), self.dim_theta())
        ).tocsc()

    def _sin_theta_div_operator(self, div, off=0.0):
        """
        Returns
        -------
        ndarray
            Returns the :math:`\\sin (\\theta+off)/div` operator
        """
        sin_theta_div_vals = np.sin((self.theta_grid.make_linspace() + off) / div)
        return sparse.dia_matrix(
            (sin_theta_div_vals, [0]), shape=(self.dim_theta(), self.dim_theta())
        ).tocsc()

    def _kron3(self, mat1, mat2, mat3):
        """
        Returns
        -------
        ndarray
            Returns the kronecker product of two operators
        """
        return sparse.kron(sparse.kron(mat1, mat2, format="csc"), mat3, format="csc")

    def _identity_phi(self):
        """
        Identity operator acting only on the :math:`\phi` Hilbert subspace.

        Returns
        -------
            scipy.sparse.csc_mat
        """
        return sparse.identity(self.dim_phi(), format="csc", dtype=np.complex_)

    def _identity_theta(self):
        """
        Identity operator acting only on the :math:`\theta` Hilbert subspace.

        Returns
        -------
            scipy.sparse.csc_mat
        """
        return sparse.identity(self.dim_theta(), format="csc", dtype=np.complex_)

    def _identity_zeta(self):
        """
        Identity operator acting only on the :math:`\theta` Hilbert subspace.

        Returns
        -------
            scipy.sparse.csc_mat
        """
        return sparse.identity(self.dim_zeta(), format="csc", dtype=np.complex_)

    def total_identity(self):
        """
        Identity operator acting only on the total Hilbert space.

        Returns
        -------
            scipy.sparse.csc_mat
        """
        return self._kron3(
            self._identity_phi(), self._identity_zeta(), self._identity_theta()
        )

    def hamiltonian(self):
        zeta_osc = self._kron3(
            self._identity_phi(),
            op.number_sparse(self.dim_zeta(), self.zeta_plasma()),
            self._identity_theta(),
        )

        phi_kinetic = self.phi_grid.second_derivative_matrix(
            prefactor=-2.0 * self.EC / (1 - self.dC ** 2)
        )
        theta_kinetic = self.theta_grid.second_derivative_matrix(
            prefactor=-2.0 * self.EC / (1 - self.dC ** 2)
        )
        cross_kinetic = (
            4
            * self.dC
            * self.EC
            / (1 - self.dC ** 2)
            * self.n_phi_operator()
            * self.n_theta_operator()
        )
        tot_kinetic = (
            self._kron3(phi_kinetic, self._identity_zeta(), self._identity_theta())
            + self._kron3(self._identity_phi(), self._identity_zeta(), theta_kinetic)
            + cross_kinetic
        )

        diag_ind = (
            0.5
            * (self.EL / (1 - self.dL) + self.EL / (1 + self.dL))
            * (self.phi_operator() ** 2 + self.theta_operator() ** 2)
        )
        off_ind = (
            self.EL
            / (1 - self.dL)
            * (
                self.phi_operator() * self.theta_operator()
                - self.theta_operator() * self.zeta_operator()
                - self.phi_operator() * self.zeta_operator()
            )
        )
        off_ind += (
            self.EL
            / (1 + self.dL)
            * (
                -self.phi_operator() * self.theta_operator()
                - self.theta_operator() * self.zeta_operator()
                + self.phi_operator() * self.zeta_operator()
            )
        )
        total_ind = diag_ind + off_ind

        junction = (
            -2
            * self.EJ
            * self._kron3(
                self._cos_phi_div_operator(1.0, 2 * np.pi * self.flux_c),
                self._identity_zeta(),
                self._cos_theta_div_operator(1.0, 2 * np.pi * self.flux_d),
            )
            - self.dJ
            * 2
            * self.EJ
            * self._kron3(
                self._sin_phi_div_operator(1.0, 2 * np.pi * self.flux_c),
                self._identity_zeta(),
                self._sin_theta_div_operator(1.0, 2 * np.pi * self.flux_d),
            )
            + 2 * self.EJ * (1 + np.abs(self.dJ)) * self.total_identity()
        )

        return zeta_osc + tot_kinetic + total_ind + junction

    def _evals_calc(self, evals_count):
        hamiltonian_mat = self.hamiltonian()
        evals = eigsh(
            hamiltonian_mat,
            k=evals_count,
            return_eigenvectors=False,
            sigma=0.0,
            which="LM",
        )
        # evals = eigsh(hamiltonian_mat, k=evals_count, return_eigenvectors=False, which='SA')
        return np.sort(evals)

    def _esys_calc(self, evals_count):
        hamiltonian_mat = self.hamiltonian()
        evals, evecs = eigsh(
            hamiltonian_mat,
            k=evals_count,
            return_eigenvectors=True,
            sigma=0.0,
            which="LM",
        )
        evals, evecs = spec_utils.order_eigensystem(evals, evecs)
        return evals, evecs

    def wavefunction(
        self, esys=None, which=0, phi_grid=None, zeta_grid=None, theta_grid=None
    ):
        evals_count = max(which + 1, 3)
        if esys is None:
            _, evecs = self.eigensys(evals_count)
        else:
            _, evecs = esys

        phi_grid = phi_grid or self.phi_grid
        zeta_grid = zeta_grid or self.zeta_grid
        theta_grid = theta_grid or self.theta_grid

        state_amplitudes = evecs[:, which].reshape(
            self.dim_phi(), self.dim_zeta(), self.dim_theta()
        )

        zeta_osc_amplitudes = np.zeros(
            (self.dim_zeta(), zeta_grid.pt_count), dtype=np.complex_
        )
        for i in range(self.dim_zeta()):
            zeta_osc_amplitudes[i, :] = osc.harm_osc_wavefunction(
                i, zeta_grid.make_linspace(), self.zeta_osc()
            )

        wavefunc_amplitudes = np.swapaxes(
            np.tensordot(zeta_osc_amplitudes, state_amplitudes, axes=([0], [1])), 0, 1
        )
        wavefunc_amplitudes = spec_utils.standardize_phases(wavefunc_amplitudes)

        grid3d = discretization.GridSpec(
            np.asarray(
                [
                    [phi_grid.min_val, phi_grid.max_val, phi_grid.pt_count],
                    [zeta_grid.min_val, zeta_grid.max_val, zeta_grid.pt_count],
                    [theta_grid.min_val, theta_grid.max_val, theta_grid.pt_count],
                ]
            )
        )
        return storage.WaveFunctionOnGrid(grid3d, wavefunc_amplitudes)

    def plot_phi_theta_wavefunction(
        self,
        esys=None,
        which=0,
        phi_grid=None,
        theta_grid=None,
        mode="abs",
        zero_calibrate=True,
        **kwargs
    ):
        """
        Plots 2D phase-basis wave function at zeta = 0

        Parameters
        ----------
        esys: ndarray, ndarray
            eigenvalues, eigenvectors as obtained from `.eigensystem()`
        which: int, optional
            index of wave function to be plotted (default value = (0)
        phi_grid: Grid1d, option
            used for setting a custom grid for phi; if None use self._default_phi_grid
        theta_grid: Grid1d, option
            used for setting a custom grid for theta; if None use self._default_theta_grid
        mode: str, optional
            choices as specified in `constants.MODE_FUNC_DICT` (default value = 'abs_sqr')
        zero_calibrate: bool, optional
            if True, colors are adjusted to use zero wavefunction amplitude as the neutral color in the palette
        **kwargs:
            plot options

        Returns
        -------
        Figure, Axes
        """
        phi_grid = phi_grid or self.phi_grid
        zeta_grid = discretization.Grid1d(0, 0, 1)
        theta_grid = theta_grid or self.theta_grid

        amplitude_modifier = constants.MODE_FUNC_DICT[mode]
        wavefunc = self.wavefunction(
            esys,
            phi_grid=phi_grid,
            zeta_grid=zeta_grid,
            theta_grid=theta_grid,
            which=which,
        )

        wavefunc.gridspec = discretization.GridSpec(
            np.asarray(
                [
                    [theta_grid.min_val, theta_grid.max_val, theta_grid.pt_count],
                    [phi_grid.min_val, phi_grid.max_val, phi_grid.pt_count],
                ]
            )
        )
        wavefunc.amplitudes = amplitude_modifier(
            spec_utils.standardize_phases(
                wavefunc.amplitudes.reshape(phi_grid.pt_count, theta_grid.pt_count)
            )
        )

        fig, axes = plot.wavefunction2d(
            wavefunc, zero_calibrate=zero_calibrate, **kwargs
        )
        # axes.set_xlim([-2 * np.pi, 2 * np.pi])
        # axes.set_ylim([-1 * np.pi, 3 * np.pi])
        axes.set_ylabel(r"$\phi$")
        axes.set_xlabel(r"$\theta$")
        axes.set_xticks([-np.pi, 0, np.pi])
        axes.set_xticklabels(["-$\pi$", "$0$", "$\pi$"])
        axes.set_yticks([0, np.pi, 2 * np.pi])
        axes.set_yticklabels(["0", "$\pi$", "$2\pi$"])

        return fig, axes

    def phase_ind_1_operator(self):
        """
        phase drop on inductor 1, used in inductive loss calculation
        """
        return -self.phi_operator() - self.theta_operator() + self.zeta_operator()

    def phase_ind_2_operator(self):
        """
        phase drop on inductor 2, used in inductive loss calculation
        """
        return -self.phi_operator() + self.theta_operator() - self.zeta_operator()

    def phase_ind_a_operator(self):
        """
        phase drop on additional inductor, used in inductive loss calculation
        """
        return self.zeta_operator()

    def q_ind(self, energy):
        """
        Frequency dependent quality factor for inductive loss
        """
        q_ind_0 = 500 * 1e6
        return (
            q_ind_0
            * kn(0, 0.5 / 2.0 / self.kbt)
            * np.sinh(0.5 / 2.0 / self.kbt)
            / kn(0, energy / 2.0 / self.kbt)
            / np.sinh(energy / 2.0 / self.kbt)
        )

    def charge_jj_1_operator(self):
        """
        charge across junction 1, used in capacitive loss calculation
        """
        return (self.n_phi_operator() + self.n_theta_operator()) / 2.0

    def charge_jj_2_operator(self):
        """
        charge across junction 2, used in capacitive loss calculation
        """
        return (self.n_phi_operator() - self.n_theta_operator()) / 2.0

    def sin_phase_jj_1_2_operator(self):
        """
        sin(phase_jj_1/2) operator, used in quasiparticle loss calculation
        """
        cos_phi_2 = self._kron3(
            self._cos_phi_div_operator(2.0, np.pi * (self.flux_c + self.flux_d)),
            self._identity_zeta(),
            self._identity_theta(),
        )
        sin_phi_2 = self._kron3(
            self._sin_phi_div_operator(2.0, np.pi * (self.flux_c + self.flux_d)),
            self._identity_zeta(),
            self._identity_theta(),
        )
        cos_theta_2 = self._kron3(
            self._identity_phi(),
            self._identity_zeta(),
            self._cos_theta_div_operator(2.0),
        )
        sin_theta_2 = self._kron3(
            self._identity_phi(),
            self._identity_zeta(),
            self._sin_theta_div_operator(2.0),
        )

        return sin_phi_2 * cos_theta_2 + cos_phi_2 * sin_theta_2

    def sin_phase_jj_2_2_operator(self):
        """
        sin(phase_jj_2/2) operator, used in quasiparticle loss calculation
        """
        cos_phi_2 = self._kron3(
            self._cos_phi_div_operator(2.0, np.pi * (self.flux_c - self.flux_d)),
            self._identity_zeta(),
            self._identity_theta(),
        )
        sin_phi_2 = self._kron3(
            self._sin_phi_div_operator(2.0, np.pi * (self.flux_c - self.flux_d)),
            self._identity_zeta(),
            self._identity_theta(),
        )
        cos_theta_2 = self._kron3(
            self._identity_phi(),
            self._identity_zeta(),
            self._cos_theta_div_operator(2.0),
        )
        sin_theta_2 = self._kron3(
            self._identity_phi(),
            self._identity_zeta(),
            self._sin_theta_div_operator(2.0),
        )

        return sin_phi_2 * cos_theta_2 - cos_phi_2 * sin_theta_2

    def y_qp(self, energy):
        """
        frequency dependent addimitance for quasiparticle loss
        """
        gap = 80.0
        xqp = 1e-8
        return (
            16
            * np.pi
            * np.sqrt(2 / np.pi)
            / gap
            * energy
            * (2 * gap / energy) ** 1.5
            * xqp
            * np.sqrt(energy / 2 / self.kbt)
            * kn(0, energy / 2 / self.kbt)
            * np.sinh(energy / 2 / self.kbt)
        )

    def q_cap(self, energy):
        """
        Frequency dependent quality factor of capacitance loss
        """

        # parameters from the Devoret paper
        q_cap_0 = 1 * 1e6
        return q_cap_0 * (6 / energy) ** 0.7

        # parameters from the Schuster paper
        # return 1 / (8e-6)

        # parameters from the Vlad paper
        # q_cap_0 = 1 / (3 * 1e-6)
        # return q_cap_0 * (6 / energy) ** 0.15

    def thermal_factor(self, energy):
        """
        thermal factor for upward and downward transition
        """
        return np.where(
            energy > 0,
            0.5 * (1 / (np.tanh(energy / 2.0 / self.kbt)) + 1),
            0.5 * (1 / (np.tanh(-energy / 2.0 / self.kbt)) - 1),
        )

    def get_t1_capacitive_loss(self, init_state):
        """
        T1 capacitive loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "charge_jj_1_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "charge_jj_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)

        s_vv_1 = (
            2
            * np.pi
            * 16
            * self.EC
            / (1 - self.dC)
            / self.q_cap(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_vv_2 = (
            2
            * np.pi
            * 16
            * self.EC
            / (1 + self.dC)
            / self.q_cap(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_cap_1 = np.abs(matelem_1) ** 2 * s_vv_1
        gamma1_cap_2 = np.abs(matelem_2) ** 2 * s_vv_2

        gamma1_cap_tot = np.sum(gamma1_cap_1) + np.sum(gamma1_cap_2)
        return 1 / (gamma1_cap_tot) * 1e-6

    def get_t1_inductive_loss(self, init_state):
        """
        T1 inductive loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "phase_ind_1_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "phase_ind_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)
        matelem_a = self.get_matelements_vs_paramvals(
            "phase_ind_a_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_a = np.delete(matelem_a, init_state)

        s_ii_1 = (
            2
            * np.pi
            * 2
            * self.EL
            / (1 - self.dL)
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_ii_2 = (
            2
            * np.pi
            * 2
            * self.EL
            / (1 + self.dL)
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_ii_a = (
            2
            * np.pi
            * 2
            * self.ELA
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_ind_1 = np.abs(matelem_1) ** 2 * s_ii_1
        gamma1_ind_2 = np.abs(matelem_2) ** 2 * s_ii_2
        gamma1_ind_a = np.abs(matelem_a) ** 2 * s_ii_a

        gamma1_ind_tot = (
            np.sum(gamma1_ind_1) + np.sum(gamma1_ind_2) + np.sum(gamma1_ind_a)
        )
        return 1 / (gamma1_ind_tot) * 1e-6

    def get_t1_qp_loss(self, init_state):
        """
        T1 quasiparticle loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "sin_phase_jj_1_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "sin_phase_jj_2_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)

        s_qp_1 = (
            self.EJ
            * (1 - self.dJ)
            * self.y_qp(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_qp_2 = (
            self.EJ
            * (1 + self.dJ)
            * self.y_qp(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_qp_1 = np.abs(matelem_1) ** 2 * s_qp_1
        gamma1_qp_2 = np.abs(matelem_2) ** 2 * s_qp_2

        gamma1_qp_tot = np.sum(gamma1_qp_1) + np.sum(gamma1_qp_2)
        return 1 / (gamma1_qp_tot) * 1e-6

    def get_t2_flux_c_noise(self, init_state):
        """
        common flux noise
        """
        delta = 1e-6
        pts = 11
        flux_c_list = np.linspace(self.flux_c - delta, self.flux_c + delta, pts)
        energy = self.get_spectrum_vs_paramvals(
            "flux_c", flux_c_list, evals_count=init_state + 2, subtract_ground=True
        ).energy_table[:, init_state]
        first_derivative = np.gradient(energy, flux_c_list)[int(np.round(pts / 2))]
        second_derivative = np.gradient(np.gradient(energy, flux_c_list), flux_c_list)[
            int(np.round(pts / 2))
        ]

        first_order = 3e-6 * np.abs(first_derivative)
        second_order = 9e-12 * np.abs(second_derivative)
        print(np.abs(second_derivative))
        return np.abs(1 / (first_order + second_order) * 1e-6) / (
            2 * np.pi
        )  # unit in ms

    def get_t2_flux_d_noise(self, init_state):
        """
        differential flux noise
        """
        delta = 1e-6
        pts = 11
        flux_d_list = np.linspace(self.flux_d - delta, self.flux_d + delta, pts)
        energy = self.get_spectrum_vs_paramvals(
            "flux_d", flux_d_list, evals_count=init_state + 2, subtract_ground=True
        ).energy_table[:, init_state]
        first_derivative = np.gradient(energy, flux_d_list)[int(np.round(pts / 2))]
        second_derivative = np.gradient(np.gradient(energy, flux_d_list), flux_d_list)[
            int(np.round(pts / 2))
        ]

        first_order = 3e-6 * np.abs(first_derivative)
        second_order = 9e-12 * np.abs(second_derivative)
        return np.abs(1 / (first_order + second_order) * 1e-6) / (
            2 * np.pi
        )  # unit in ms

    def current_noise_operator(self):
        return -2 * self._kron3(
            self._cos_phi_div_operator(1.0),
            self._identity_zeta(),
            self._cos_theta_div_operator(1.0),
        )

    def get_t2_current_noise(self, init_state):
        """
        T2 critical current noise
        """
        delta = 1e-7
        pts = 11
        ej_list = np.linspace(self.EJ - delta, self.EJ + delta, pts)
        energy = self.get_spectrum_vs_paramvals(
            "EJ", ej_list, evals_count=init_state + 2, subtract_ground=True
        ).energy_table[:, init_state]
        first_derivative = np.gradient(energy, ej_list)[int(np.round(pts / 2))]
        return np.abs(1 / (5e-7 * self.EJ * np.abs(first_derivative)) * 1e-6) / (
            2 * np.pi
        )  # unit in ms

    def print_noise(self, g_state, e_state, table=True):
        """
        print summary of all noise channels
        :param g_state: the logical 0 state of the qubit
        :param e_state: the logical 1 state of the qubit
        :return: t2_current, t2_flux, t2_fluxa, t1_cap, t1_ind, t1_qp, t1_tot, t2_tot
        """
        t2_current = self.get_t2_current_noise(e_state)
        t2_flux_c = self.get_t2_flux_c_noise(e_state)
        t2_flux_d = self.get_t2_flux_d_noise(e_state)
        t1_cap = 1 / (
            1 / self.get_t1_capacitive_loss(g_state)
            + 1 / self.get_t1_capacitive_loss(e_state)
        )
        t1_ind = 1 / (
            1 / self.get_t1_inductive_loss(g_state)
            + 1 / self.get_t1_inductive_loss(e_state)
        )
        t1_qp = 1 / (
            1 / self.get_t1_qp_loss(g_state) + 1 / self.get_t1_qp_loss(e_state)
        )
        t1_tot = 1 / (1 / t1_cap + 1 / t1_ind + 1 / t1_qp)
        t2_tot = 1 / (1 / t2_current + 1 / t2_flux_c + 1 / t2_flux_d + 1 / t1_tot / 2)

        if table is True:
            print(
                " T2_current =",
                t2_current,
                " ms",
                "\n T2_flux_c =",
                t2_flux_c,
                " ms",
                "\n T2_flux_d =",
                t2_flux_d,
                " ms",
                "\n T1_cap =",
                t1_cap,
                " ms",
                "\n T1_ind =",
                t1_ind,
                " ms",
                "\n T1_qp =",
                t1_qp,
                " ms",
                "\n T1 =",
                t1_tot,
                " ms",
                "\n T2 =",
                t2_tot,
                " ms",
            )

        return np.array(
            [t2_current, t2_flux_c, t2_flux_d, t1_cap, t1_ind, t1_qp, t1_tot, t2_tot]
        )

    def get_t1_capacitive_loss_channel(self, init_state):
        """
        T1 capacitive loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "charge_jj_1_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "charge_jj_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)

        s_vv_1 = (
            2
            * np.pi
            * 16
            * self.EC
            / (1 - self.dC)
            / self.q_cap(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_vv_2 = (
            2
            * np.pi
            * 16
            * self.EC
            / (1 + self.dC)
            / self.q_cap(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_cap_1 = np.abs(matelem_1) ** 2 * s_vv_1
        gamma1_cap_2 = np.abs(matelem_2) ** 2 * s_vv_2

        gamma1_cap_tot = gamma1_cap_1 + gamma1_cap_2
        return 1 / (gamma1_cap_tot) * 1e-6

    def get_t1_inductive_loss_channel(self, init_state):
        """
        T1 inductive loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "phase_ind_1_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "phase_ind_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)
        matelem_a = self.get_matelements_vs_paramvals(
            "phase_ind_a_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_a = np.delete(matelem_a, init_state)

        s_ii_1 = (
            2
            * np.pi
            * 2
            * self.EL
            / (1 - self.dL)
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_ii_2 = (
            2
            * np.pi
            * 2
            * self.EL
            / (1 + self.dL)
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_ii_a = (
            2
            * np.pi
            * 2
            * self.ELA
            / self.q_ind(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_ind_1 = np.abs(matelem_1) ** 2 * s_ii_1
        gamma1_ind_2 = np.abs(matelem_2) ** 2 * s_ii_2
        gamma1_ind_a = np.abs(matelem_a) ** 2 * s_ii_a

        gamma1_ind_tot = gamma1_ind_1 + gamma1_ind_2 + gamma1_ind_a
        return 1 / (gamma1_ind_tot) * 1e-6

    def get_t1_qp_loss_channel(self, init_state):
        """
        T1 quasiparticle loss of one particular state
        """
        cutoff = init_state + 4
        energy = self._evals_calc(cutoff)
        energy_diff = energy[init_state] - energy
        energy_diff = np.delete(energy_diff, init_state)

        matelem_1 = self.get_matelements_vs_paramvals(
            "sin_phase_jj_1_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_1 = np.delete(matelem_1, init_state)
        matelem_2 = self.get_matelements_vs_paramvals(
            "sin_phase_jj_2_2_operator", "ph", [0], evals_count=cutoff
        ).matrixelem_table[0, init_state, :]
        matelem_2 = np.delete(matelem_2, init_state)

        s_qp_1 = (
            self.EJ
            * (1 - self.dJ)
            * self.y_qp(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )
        s_qp_2 = (
            self.EJ
            * (1 + self.dJ)
            * self.y_qp(np.abs(energy_diff))
            * self.thermal_factor(energy_diff)
        )

        gamma1_qp_1 = np.abs(matelem_1) ** 2 * s_qp_1
        gamma1_qp_2 = np.abs(matelem_2) ** 2 * s_qp_2

        gamma1_qp_tot = gamma1_qp_1 + gamma1_qp_2
        return 1 / (gamma1_qp_tot) * 1e-6

    def get_noise_channel(self, init_state):
        inductive_loss = self.get_t1_inductive_loss_channel(init_state)
        capacitive_loss = self.get_t1_capacitive_loss_channel(init_state)
        qp_loss = self.get_t1_qp_loss_channel(init_state)

        return 1 / (1 / inductive_loss + 1 / capacitive_loss + 1 / qp_loss)
