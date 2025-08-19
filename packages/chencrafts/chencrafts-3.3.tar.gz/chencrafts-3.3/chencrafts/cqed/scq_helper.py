__all__ = [
    'wavefunc_FT',
]

import numpy as np
from scipy.fft import fft, fftfreq

from scqubits.core.storage import WaveFunction
from scqubits.core.namedslots_array import NamedSlotsNdarray, Parameters
import scqubits as scq

from typing import List, Tuple, Literal, OrderedDict


def wavefunc_FT(
    x_list: List | np.ndarray, 
    amp_x: List | np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    x_list = np.array(x_list)
    amp_x = np.array(amp_x)

    x0, x1 = x_list[0], x_list[-1]
    dx = x_list[1] - x_list[0]

    amp_p_dft = fft(amp_x)
    n_list = fftfreq(amp_x.size) * 2 * np.pi / dx

    # In order to get a discretisation of the continuous Fourier transform
    # we need to multiply amp_p_dft by a phase factor
    amp_p = amp_p_dft * dx * np.exp(-1j * n_list * x0) / (np.sqrt(2*np.pi))

    return n_list, amp_p
