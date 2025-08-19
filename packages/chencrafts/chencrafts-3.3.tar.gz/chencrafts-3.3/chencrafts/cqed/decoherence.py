__all__ = [
    'thermal_ratio',
    'n_th',
    'thermal_factor',
    'readout_error',
    'qubit_addi_energy_relax_w_res',
    'qubit_shot_noise_dephasing_w_res',
    'purcell_factor',
    'driven_osc_steady_alpha',
    'qubit_relax_from_drive_port',
    'S_quantum_johnson_nyquist',
    't1_charge_line_impedance',
]

import numpy as np
import qutip as qt
from scqubits.core.hilbert_space import HilbertSpace
from scqubits.core.qubit_base import QubitBaseClass
from scipy.special import erfc
from scipy.constants import h, k, hbar, e
from numpy.typing import ArrayLike

from typing import Tuple, Callable, List
from chencrafts.cqed.mode_assignment import single_mode_dressed_esys


def thermal_ratio(
    freq: float | np.ndarray, 
    temp: float | np.ndarray,
) -> float | np.ndarray:
    """
    Return the thermal ratio hbar * omega / k_B T.
    
    Parameters
    ----------
    freq: float | np.ndarray
        The frequency of the interested transition, in GHz
    temp: float | np.ndarray
        The temperature of the environment, in Kelvin

    Returns
    -------
    float | np.ndarray
        Thermal ratio
    """
    return (h * freq * 1e9) / (k * temp)

def n_th(
    freq: float | np.ndarray, 
    temp: float | np.ndarray, 
    n_th_base: float | np.ndarray = 0.0
) -> float | np.ndarray:
    """
    Calculate the thermal occupation number of a mode at a given temperature
    (Bose-Einstein factor).
    Equals to thermal_factor(-freq, temp) or (thermal_factor(freq, temp) - 1)
    
    Parameters
    ----------
    freq: float | np.ndarray
        The frequency of the interested transition, must be non-negative, in GHz
    temp: float | np.ndarray
        The temperature of the environment, in Kelvin
    n_th_base: float | np.ndarray
        Sometimes adding a constant to the thermal occupation number is necessary
        to fit the experimental data. This parameter is used to do so.

    Returns
    -------
    float | np.ndarray
        Thermal occupation number
    
    """
    assert np.all(freq >= 0), "Frequency must be non-negative"
    return 1 / (np.exp(thermal_ratio(freq, temp)) - 1) + n_th_base

def thermal_factor(omega, T):
    """
    Return the Boltzmann thermal factor in considering a decoherence rate.
    Equals to (n_th(freq, temp) + 1) when freq is positive or 
    n_th(abs(freq), temp) = - (n_th(freq, temp) + 1) when freq is negative.
    
    Parameters
    ----------
    omega: float | np.ndarray
        The frequency of the interested transition, in GHz
    T: float | np.ndarray
        The temperature of the environment, in Kelvin

    Returns
    -------
    float | np.ndarray
        Thermal factor
    """
    therm_ratio = thermal_ratio(omega, T)
    return (
        1 / np.tanh(0.5 * np.abs(therm_ratio))
        / (1 + np.exp(-therm_ratio))
    )

def readout_error(
    n: float | np.ndarray, 
    relax_rate: float | np.ndarray,
    int_time: float | np.ndarray,
) -> float | np.ndarray:
    """
    Calculate the readout error probability of a qubit with a given dispersive shift,
    relaxation rate and integration time.

    Parameters
    ----------
    n: float | np.ndarray
        The average resonator photon number during readout
    relax_rate: float | np.ndarray
        The relaxation rate of the resonator, in GHz
    int_time: float | np.ndarray
        The integration time of the readout, in ns

    Returns
    -------
    float | np.ndarray
        Readout error probability
    """

    SNR = 2 * np.abs(n) * np.sqrt(relax_rate * int_time)
    return 0.5 * erfc(SNR / 2)

def qubit_addi_energy_relax_w_res(
    qubit_relax_rate: float | np.ndarray, 
    qubit_deph_rate: float | np.ndarray,
    g_over_delta: float | np.ndarray, 
    readout_photon_num: float | np.ndarray, 
    n_crit: float | np.ndarray, 
    res_relax_rate: float | np.ndarray, 
) -> Tuple[float | np.ndarray, float | np.ndarray]:
    """
    Following Boissonneault et al. (2009), equation (5.7) and (5.8).

    The returned value is a tuple of relaxation rate and excitation rate when the qubit 
    is coupled with a resonator with some photons in it. 
    
    Qubit natural relaxation rate is NOT included in the returned value.

    Parameters
    ----------
    qubit_relax_rate: float | np.ndarray
        Qubit relaxation rate, in GHz
    qubit_deph_rate: float | np.ndarray
        Qubit dephasing rate, in GHz
    g_over_delta: float | np.ndarray
        Coupling strength devided by detuning
    readout_photon_num: float | np.ndarray
        Number of photons in the resonator
    n_crit: float | np.ndarray
        Critical photon number of the resonator
    res_relax_rate: float | np.ndarray
        Resonator relaxation rate, in GHz

    Returns
    -------
    Tuple[float | np.ndarray, float | np.ndarray]
        Readout introduced relaxation rate and excitation rate
    """
    # in the Equation (5.7), the "0" should be "1". The change here is to make the expression
    # exclude the qubit natural relaxation rate. 
    k_down_ro = (
        qubit_relax_rate * (0 - (readout_photon_num + 0.5) / 2 / n_crit)
        + g_over_delta**2 * res_relax_rate
        + 2 * g_over_delta**2 * qubit_deph_rate * (readout_photon_num + 1)
    )
    k_up_ro = 2 * g_over_delta**2 * qubit_deph_rate * readout_photon_num
    return k_down_ro, k_up_ro

def qubit_shot_noise_dephasing_w_res(
    res_relax_rate, chi, n_th_r,
    drive_strength = 0.0, drive_detuning = 0.0,
) -> float | np.ndarray:
    """
    Follow Clerk and Utami (2007), Equation (43), (44), (66) and (69).

    The returned value is the dephasing rate of a qubit coupled with a resonator
    when the resonator is excited by a the environment and a drive.

    Parameters
    ----------
    res_relax_rate: float | np.ndarray
        Resonator relaxation rate, in GHz
    chi: float | np.ndarray
        Dispersice shift of the qubit-resonator system, in GHz
    n_th_r: float | np.ndarray  
        Thermal occupation number of the resonator when not driven
    drive_strength: float | np.ndarray
        Drive strength of the resonator, in GHz
    drive_detuning: float | np.ndarray
        Drive detuning of the resonator, in GHz

    Returns
    -------
    float | np.ndarray
        Dephasing rate of the qubit

    """
    # Equation (44) depahsing rate without drive
    Gamma_phi_th = res_relax_rate / 2 * (np.sqrt(
        (1 + 2j * chi / res_relax_rate)**2 + 8j * chi * n_th_r / res_relax_rate
    ) - 1).real

    if drive_strength != 0.0:
        # Equation (43) qubit frequency shift
        Delta_th = res_relax_rate / 2 * (np.sqrt(
            (1 + 2j * chi / res_relax_rate)**2 + 8j * chi * n_th_r / res_relax_rate
        )).imag
        # Equation (69) depahsing rate with drive
        gamma_th = res_relax_rate + 2 * Gamma_phi_th
        Gamma_phi_dr = (
            drive_strength**2 / 2 * chi * Delta_th * gamma_th 
            / ((drive_detuning + Delta_th)**2 + (gamma_th / 2)**2)
            / ((drive_detuning - Delta_th)**2 + (gamma_th / 2)**2)
        )

        Gamma_phi = Gamma_phi_th + Gamma_phi_dr
    else:
        Gamma_phi = Gamma_phi_th

    return Gamma_phi

def purcell_factor(
    hilbertspace: HilbertSpace,
    res_mode_idx: int, qubit_mode_idx: int, 
    res_state_func: Callable | int = 0, qubit_state_index: int = 0,
    collapse_op_list: List[qt.Qobj] = [],
    dressed_indices: np.ndarray | None = None, eigensys = None,
    **kwargs
) -> List[float]:
    """
    It returns some factors between two mode: osc and qubit, in order to 
    calculate the decay rate of the state's occupation probability. The returned numbers, 
    say, n_osc and n_qubit, can be used in this way:  
     - state's decay rate = n_osc * osc_decay_rate + n_qubit * qubit_decay_rate

    Parameters
    ----------
    osc_mode_idx, qubit_mode_idx:
        The index of the two modes in the hilberspace's subsystem_list
    osc_state_func, qubit_state_index:
        The purcell decay rate of a joint system when the joint state can be described by 
        some bare product state of osc and B. Those two arguments can be an integer
        (default, 0), indicating a bare fock state. Additionally, A_state_func can
        also be set to a function with signature `osc_state_func(<some basis of osc mode>, 
        **kwargs)`. Such a fuction should check the validation of the basis, and raise a
        RuntimeError if invalid.
    dressed_indeces: 
        An array mapping the FLATTENED bare state label to the eigenstate label. Usually
        given by `ParameterSweep["dressed_indices"]`.
    eigensys: 
        The eigensystem for the hilbertspace.
    collapse_op_list:
        If empty, the purcell factors will be evaluated assuming the collapse operators
        are osc mode's annilation operator and qubit mode's sigma_minus operator. Otherwise,
        will calculate the factors using operators specified by the user by:
         - factor = qutip.expect(operator, state) for all operators
    kwargs:
        kwyword arguments for osc_state_func

    Returns
    -------
    Purcell factors
    """

    # obtain collapse operators
    if collapse_op_list == []:
        collapse_op_list = [
            hilbertspace.annihilate(hilbertspace.subsystem_list[res_mode_idx]),
            hilbertspace.hubbard_operator(0, 1, hilbertspace.subsystem_list[qubit_mode_idx])
        ]

    # Construct the desired state
    state_label = np.zeros_like(hilbertspace.subsystem_dims, dtype=int)
    state_label[qubit_mode_idx] = qubit_state_index

    _, osc_evecs = single_mode_dressed_esys(
        hilbertspace,
        res_mode_idx,
        tuple(state_label),
        dressed_indices,
        eigensys,
    )
    try: 
        if callable(res_state_func):
            state = res_state_func(osc_evecs, **kwargs)
        else:
            state = osc_evecs[res_state_func]
    except (RuntimeError, IndexError):
        # if the state is invalid
        return [np.nan] * len(collapse_op_list)
        
    # calculate expectation value of collapse operators
    factor_list = []
    for op in collapse_op_list:
        factor_list.append(
            qt.expect(op.dag() * op, state)
        )

    return factor_list

def driven_osc_steady_alpha(
    drive_strength: float,
    drive_detuning: float,
    decay_rate: float,
) -> float:
    """
    Steady state displacement of a driven oscillator.
    
    Parameters
    ----------
    drive_strength: float
        Drive strength of the oscillator, in GHz. 
        Note the following difference: 
        H = eps * (a + adag) * cos(omega * t) --> drive_strength = eps / 2
        H = eps * a * exp(-i * omega * t) + h.c. --> drive_strength = eps
    drive_detuning: float
        Drive_freq - osc_freq, in GHz
    decay_rate: float
        Decay rate of the oscillator, in GHz. Note that it is 1 / T1 / 2pi.

    Returns
    -------
    float
        Steady state displacement of the oscillator
    """
    return (
        - drive_strength 
        / (drive_detuning - 1j * decay_rate / 2)
    )

# Drive port noise induced qubit relaxation
def qubit_relax_from_drive_port(
    f_q: float,
    chi: ArrayLike,
    matelem: ArrayLike,
    S_V: Callable,
) -> float:
    """
    General expression for decay rate.

    Parameters
    ----------
    f_q : float
        The qubit frequency in GHz.
    chi : ArrayLike
        The susceptibility of the qubit drive parameter g wrt the input voltage. 
        Unit of g is defined such that g * matelem has dimension of energy.
        So the unit of chi is <energy>/<matelem>/V.
    matelem : ArrayLike
        The matrix element of the qubit operator. The unit of g*matelem is energy.
    S_V : Callable
        The voltage noise spectral density in V^2/GHz, should be a function of frequency in GHz, i.e. S_V(f).

    Returns
    -------
    The decay rate in GHz
    """
    matelem = np.array(matelem)
    chi = np.array(chi)
    gamma = (
        (1 / hbar**2) 
        * np.abs(np.sum(chi * matelem)) ** 2 
        * S_V(f_q) / 1e9    # V^2/GHz ---> V^2/Hz
    ) / 1e9                # Hz ---> GHz
    return gamma

def S_quantum_johnson_nyquist(f: float, T: float, Z_0: float) -> float:
    """
    The quantum Johnson-Nyquist noise spectral density.

    Parameters
    ----------
    f : float
        The frequency in GHz.
    T : float
        The temperature in K.
    Z_0 : float
        The impedance in Ohm.

    Returns
    -------
    The spectral density in V^2/GHz
    """
    return (
        2 * h 
        * np.abs(f) * 1e9   # GHz ---> Hz
        * Z_0 
        * thermal_factor(f, T)
    ) * 1e9        # V^2/Hz --> V^2/GHz

def t1_charge_line_impedance(
    qubit: QubitBaseClass,
    i: int,
    j: int,
    Z0: float,
    T: float,
    C_g: float,
    C_f: float,
    total_rate: bool = True,
    get_rate: bool = False,
):
    """ 
    Calculate the relaxation time T1 due to charge line for a qubit.

    Parameters
    ----------
    i : int
        The index of the initial state.
    j : int
        The index of the final state.
    qubit : QubitBaseClass
        The qubit object.
    Z0 : float
        The impedance of the port in Ohm.
    T : float
        The temperature in K.
    C_g : float
        The gate capacitance in fF.
    C_f : float
        The qubit (fluxonium) capacitance in fF.
    total_rate : bool
        If True, the total rate is calculated. If False, only the rate from i to j is calculated.
    get_rate : bool
        If True, return the rate. If False, return the relaxation time T1.
    
    Returns
    -------
        The relaxation time T1 in ns, or the rate in GHz.
    """
    n_matelem = qubit.matrixelement_table("n_operator", evals_count=max(i, j) + 1)
    n_matelem_ij = n_matelem[j, i]
    eigenvals = qubit.eigenvals(evals_count=max(i, j) + 1)
    freq_ij = eigenvals[i] - eigenvals[j]
    chi = 2 * e * C_g / C_f
    rate_ij = qubit_relax_from_drive_port(
        f_q=freq_ij,
        chi=chi,
        matelem=n_matelem_ij,
        S_V=lambda f, T=T, Z0=Z0: S_quantum_johnson_nyquist(f, T, Z0),
    )
    rate_final = rate_ij
    if total_rate:
        rate_ji = qubit_relax_from_drive_port(
            f_q=-freq_ij,
            chi=chi,
            matelem=n_matelem[i, j],
            S_V=lambda f, T=T, Z0=Z0: S_quantum_johnson_nyquist(f, T, Z0),
        )
        rate_final += rate_ji
    if get_rate:
        return rate_final
    return 1 / rate_final