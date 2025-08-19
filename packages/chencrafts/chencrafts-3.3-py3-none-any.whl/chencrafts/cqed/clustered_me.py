__all__ = [
    "ohmic_spectral_density",
    "q_cap_fun",
    "cap_spectral_density",
    "q_ind_fun",
    "ind_spectral_density",
    "delta_spectral_density",
    "MEConstructor",
]

import numpy as np
import qutip as qt
import scipy as sp
import scqubits as scq
from scqubits.core.param_sweep import ParameterSweep
from scqubits.core.namedslots_array import NamedSlotsNdarray
from scqubits.io_utils.fileio_qutip import QutipEigenstates
import networkx as nx

from chencrafts.cqed.decoherence import thermal_ratio, thermal_factor

from typing import List, Tuple, Any, Dict, Callable


# When considering dephasing, we only consider the zero-frequency transition
# because the noise spectral density is 1/f.
TPHI_HI_FREQ_CUTOFF = 1e-8

# When considering depolarization, we limit the lowest frequency, or the 
# thermal factor blows up.
T1_LO_FREQ_CUTOFF = 1e-2

# When encountering rate small than this threshold, we directly ignore the
# jump operator.
RATE_THRESHOLD = 1e-10  # unit (rad/ns)

# When clustering two transitions, we set a threshold for the transition frequency
# difference, in GHz. Besides, we also assume the spectral density is flat,
# which is quantified by a relative tolerance.
JUMP_FREQ_ATOL = 0.001
SPEC_DENS_RTOL = 0.1


# Pre-defined spectral density ================================================
def ohmic_spectral_density(omega, T, Q = 10e6):
    """
    Return the ohmic spectral density that is linearly dependent on frequency.
    
    Parameters
    ----------
    omega: float | np.ndarray
        The frequency of the noise, GHz.
    T: float | np.ndarray
        The temperature of the noise, K.
    Q: float | np.ndarray
        The quality factor.

    Returns
    -------
    float | np.ndarray
        The ohmic spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    therm_factor = thermal_factor(omega, T)
    return np.pi * 2 * np.abs(omega) / Q * therm_factor

def q_cap_fun(omega, T, Q_cap = 1e6):
    """
    See Smith et al (2020). Return the capacitive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    Q_cap: float
        The quality factor of the capacitor.

    Returns
    -------
    float
        The capacitive noise's spectral density.
    """
    return (
        Q_cap
        * (6 / np.abs(omega)) ** 0.7
    )

def cap_spectral_density(omega, T, EC, Q_cap = 1e6):
    """
    Return the capacitive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    EC: float
        The charging energy of the qubit.
    Q_cap: float
        The quality factor of the capacitor.

    Returns
    -------
    float
        The capacitive noise's spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    therm_factor = thermal_factor(omega, T)
    s = (
        2
        * 8
        * EC
        / q_cap_fun(omega, T, Q_cap)
        * therm_factor
    )
    s *= (
        2 * np.pi
    )  # We assume that system energies are given in units of frequency
    return s

def q_ind_fun(omega, T, Q_ind = 500e6):
    """
    Return the inductor's quality factor.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    Q_ind: float
        The quality factor of the inductor.

    Returns
    -------
    float
        The inductor's quality factor.
    """
    therm_ratio = abs(thermal_ratio(omega, T))
    therm_ratio_500MHz = thermal_ratio(0.5, T)
    return (
        Q_ind
        * (
            sp.special.kv(0, 1 / 2 * therm_ratio_500MHz)
            * np.sinh(1 / 2 * therm_ratio_500MHz)
        )
        / (
            sp.special.kv(0, 1 / 2 * therm_ratio)
            * np.sinh(1 / 2 * therm_ratio)
        )
    )

def ind_spectral_density(omega, T, EL, Q_ind = 500e6):
    """
    Return the inductive noise's spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    T: float
        The temperature of the noise, K.
    EL: float
        The inductive energy of the qubit, GHz.
    Q_ind: float
        The quality factor of the inductor.

    Returns
    -------
    float
        The inductive noise's spectral density.
    """
    # add a cutoff to avoid zero division
    omega = np.where(np.abs(omega) < T1_LO_FREQ_CUTOFF, T1_LO_FREQ_CUTOFF, omega)
    
    therm_factor = thermal_factor(omega, T)
    s = (
        2
        * EL
        / q_ind_fun(omega, T, Q_ind)
        * therm_factor
    )
    s *= (
        2 * np.pi
    )  # We assume that system energies are given in units of frequency
    return s

def delta_spectral_density(omega, peak_value, peak_loc = 0, peak_width = 1e-10):
    """
    Obtain a delta function spectral density. It's used to model the dephasing
    noise, which have a 1/f spectrum. We assume it dies down very quickly so
    any non-zero frequency will have a zero spectral density.
    
    Parameters
    ----------
    omega: float
        The frequency of the noise, GHz.
    peak_value: float
        The value of the delta function.
    peak_loc: float
        The location of the delta function.
    peak_width: float
        The width of the delta function, for numrical purposes.

    Returns
    -------
    float
        The delta function spectral density.
    """
    if np.allclose(omega, peak_loc, atol=peak_width):
        return peak_value
    else:
        return 0

# Rate calculation based on Golden rule =======================================
class Jump:
    def __init__(
        self, 
        channel: str,
        transition: Tuple[int, int] | List[Tuple[int, int]],
        freq: float,
        spec_dens: [float],
        op: qt.Qobj,
        bare_transition: [
            Tuple[Tuple[int, ...], Tuple[int, ...]] 
            | List[Tuple[Tuple[int, ...], Tuple[Tuple[int, ...], ...]] | None]
        ] = None,
    ):
        """
        Parameters
        ----------
        channel: str
            The name of the decoherence channel.
        transition: Tuple[int, int] | List[Tuple[int, int]]
            The initial and final state eigenstate indices.
        freq: float
            The transition frequency of this jump.
        spec_dens: float
            The bath spectral density at the transition frequency.
        op: qt.Qobj
            The jump operator of this jump, which include a sqrt of the 
            transition rate.
        bare_transition: [
            Tuple[Tuple[int, ...], Tuple[int, ...]] 
            | List[Tuple[Tuple[int, ...], Tuple[Tuple[int, ...], ...]]]
        ] = None,
            Optioinal, the bare indices of the initial and final states.
        """
        self.channel = channel
        if isinstance(transition, tuple):
            self.transition = [transition]
        else:
            self.transition = transition
        self.freq = freq
        self.spec_dens = spec_dens
        self.op = op
        
        if isinstance(bare_transition, tuple):
            self.bare_transition = [bare_transition]
        elif bare_transition is None:
            self.bare_transition = [None] * len(self.transition)
        else:
            self.bare_transition = bare_transition
        
    def __add__(self, other: 'Jump') -> 'Jump':
        """
        This is only valid when two transitions are at the similar frequency,
        and the spectral density is flat.
        """
        
        transition = self.transition + other.transition
        
        return Jump(
            channel = self.channel,
            transition = transition,
            freq = self.freq,
            spec_dens = self.spec_dens,
            op = self.op + other.op,
            bare_transition = self.bare_transition + other.bare_transition,
        )
        
    def can_cluster_with(self, other: 'Jump') -> bool:
        """
        Check if two jumps can be clustered together.
        """
        if self.channel != other.channel:
            return False
        if not np.allclose(self.freq, other.freq, atol=JUMP_FREQ_ATOL):
            return False
        if not np.allclose(self.spec_dens, other.spec_dens, rtol=SPEC_DENS_RTOL):
            return False
        return True
    
    def _typical_rate(self) -> float:
        """
        Return the median of all the non-zero matrix elements of the jump operator.
        """
        op_array = self.op.full()
        non_zero_elements = ~np.isclose(op_array, 0, atol=RATE_THRESHOLD)
        return np.median(np.abs(op_array[non_zero_elements]))**2
    
    def __str__(self):
        if self.bare_transition[0] is not None:
            bare_transition_str = f"""
    bare_transition={self.bare_transition},"""
        else:
            bare_transition_str = ""
        
        return f"""Jump(
    channel={self.channel}, 
    transition={self.transition},{bare_transition_str}
    Transition frequency: {self.freq:.1e} GHz
    Typical rate: {self._typical_rate():.1e} rad/ns
)
"""
    
    def __repr__(self):
        return self.__str__()
    
class MEConstructor:
    """
    Construct a clustered master equation.
    
    Core functionality of this constructor is to construct the jump operators
    based on the system-bath coupling operator and the bath spectral density.
    
    We construct jump operators for one system-bath coupling at a time, which    
    - Take in: 
        - A system-bath coupling operator
        - Bath spectral density
    - Obtain intermediate results (for each pair of eigenstates): 
        - Transition frequency
        - Transition rate
        - Spectral density
        - Projector
    - Stores: 
        - Clustered projectors
    """
    
    def __init__(
        self, 
        hilbertspace: scq.HilbertSpace,
        truncated_dim: int = None,
        esys: Tuple[np.ndarray, QutipEigenstates] = None,
        dressed_indices: np.ndarray = None,
    ):
        self.hilbertspace = hilbertspace
        if truncated_dim is not None:
            self.truncated_dim = truncated_dim
        else:
            self.truncated_dim = hilbertspace.dimension
            
        if esys is None or dressed_indices is None:
            hilbertspace.generate_lookup(ordering="LX")
            esys = hilbertspace["evals"][0], hilbertspace["evecs"][0]
            dressed_indices = hilbertspace["dressed_indices"][0]
        self.evals, self.evecs = esys
        self.dressed_indices: np.ndarray = dressed_indices
            
        self.unclustered_jumps: Dict[str, List[Jump]] = {}
        self.clustered_jumps: Dict[str, List[Jump]] = {}
        
    def _bare_indices(
        self,
        dressed_idx: int,
    ) -> Tuple[int, ...] | None:
        """
        Convert the dressed index to the bare index.
        """
        try:
            idx_bare_ravel = np.where(
                self.dressed_indices == dressed_idx
            )[0][0]
            idx_bare = np.unravel_index(
                idx_bare_ravel,
                self.hilbertspace.subsystem_dims,
            )
        except IndexError:
            idx_bare = None
        return idx_bare
    
    def add_channel(
        self,
        channel: str,
        op: qt.Qobj,
        spec_dens_fun: Callable,
        spec_dens_kwargs: Dict[str, Any] = {},
        depolarization_only: bool = True,
        record_bare_transition: bool = True,
    ):
        """
        Construct the jump operators for a given channel, both unclustered and
        clustered.
        
        Parameters
        ----------
        channel: str
            The channel of the jump operator.
        op: qt.Qobj
            The system-bath coupling operator in the eigenbasis, typically
            obtained by `HilbertSpace.op_in_dressed_eigenbasis()`.
        spec_dens_fun: Callable
            The bath spectral density as a function of frequency, should have 
            the signature `spec_dens_fun(omega, **spec_dens_kwargs)`.
        spec_dens_kwargs: Dict[str, Any]
            The keyword arguments provided to the bath spectral density function.
        depolarization_only: bool
            Whether to only consider the depolarization channel (i.e., ignoring
            all self-transitions).
        """
        # get the transition frequency and spectral density for each pair of 
        # eigenstates
        jumps = []
        for idx_init in range(self.truncated_dim):
            for idx_final in range(self.truncated_dim):
                if idx_init == idx_final and depolarization_only:
                    continue
                
                # compute the transition rate
                freq = self.evals[idx_init] - self.evals[idx_final] # negative for upward transition
                spec_dens = spec_dens_fun(freq, **spec_dens_kwargs)
                mat_elem = op[idx_init, idx_final]
                rate = np.abs(mat_elem) ** 2 * spec_dens
                
                if rate < RATE_THRESHOLD:
                    continue
                
                # record the bare transition indices if requested
                if record_bare_transition:
                    bare_transition = (
                        self._bare_indices(idx_init),
                        self._bare_indices(idx_final),
                    )
                else:
                    bare_transition = None
                
                # construct the jump operator
                jump_op = qt.projection(
                    dimensions = self.truncated_dim,
                    n = idx_final,
                    m = idx_init,
                ) * np.sqrt(rate)
                
                # record the jump
                jumps.append(
                    Jump(
                        channel = channel,
                        transition = (idx_init, idx_final),
                        freq = freq,
                        spec_dens = spec_dens,
                        op = jump_op,
                        bare_transition = bare_transition,
                    )
                )
                
        self.unclustered_jumps[channel] = jumps
        
        self._cluster_jumps(channel)
        
    def _cluster_jumps(self, channel: str):
        """
        Cluster the jump operators that have similar transition frequency
        and spectral density.
        """
        jumps = self.unclustered_jumps[channel]
            
        # check whether two jumps can be clustered together
        compatibility_matrix = np.zeros((len(jumps), len(jumps)))
        for idx_1, jump_1 in enumerate(jumps):
            for idx_2, jump_2 in enumerate(jumps):
                if idx_1 == idx_2:
                    continue
                elif idx_1 > idx_2:
                    compatibility_matrix[idx_1, idx_2] = jump_1.can_cluster_with(jump_2)
                else:
                    compatibility_matrix[idx_1, idx_2] = compatibility_matrix[idx_2, idx_1]
                    
        # think of this as a graph, and cluster the jumps that are 
        # associated with the same connected component
        G = nx.Graph(compatibility_matrix)
        connected_components = list(nx.connected_components(G))
        
        # cluster the jumps
        clustered_jumps = []
        for connected_component in connected_components:
            for idx, jump_idx in enumerate(connected_component):
                if idx == 0:
                    jump = jumps[jump_idx]
                else:
                    jump += jumps[jump_idx]
            clustered_jumps.append(jump)
            
        self.clustered_jumps[channel] = clustered_jumps
            
    def all_clustered_jump_ops(
        self,
        lindbladian: bool = False,
    ) -> List[qt.Qobj]:
        """
        Return all the constructed jump operators.
        """
        ops = []
        for _, jumps in self.clustered_jumps.items():
            for jump in jumps:
                if lindbladian:
                    ops.append(qt.lindblad_dissipator(jump.op))
                else:
                    ops.append(jump.op)
        return ops
    
    def all_unclustered_jump_ops(
        self,
        lindbladian: bool = False,
    ) -> List[qt.Qobj]:
        """
        Return all the constructed jump operators.
        """
        ops = []
        for _, jumps in self.unclustered_jumps.items():
            for jump in jumps:
                if lindbladian:
                    ops.append(qt.lindblad_dissipator(jump.op))
                else:
                    ops.append(jump.op)
        return ops
    