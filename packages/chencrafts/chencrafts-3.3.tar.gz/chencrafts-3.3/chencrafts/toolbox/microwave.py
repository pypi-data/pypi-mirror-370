__all__ = ["TLProfile"]

import numpy as np

class TLProfile:    
    V_plus : complex
    V_minus : complex
    
    def __init__(
        self, 
        beta: float, 
        L: float, 
        Z0: float | None = None,
        **kwargs
    ):
        """
        Transmission line mode profile. It can be initialized by boundary 
        conditions
        1. V_plus and V_minus (left-moving and right-moving wave amplitudes)
        2. V_0 and V_L (voltage at x=0 and x=L)
        3. V_0 and I_0 (voltage and current at x=0)
        4. V_L and I_L (voltage and current at x=L)
    
        Parameters
        ----------
        beta: 
            propagation constant (1/L, where L is an arbitrary length unit)
        L: 
            Transmission line length (L)
        Z0: Optional
            Characteristic impedance (Ohm), needed for calculation involving current
        V_plus: Optional
            Right-moving wave voltage
        V_minus: Optional
            Left-moving wave voltage
        V_0: Optional
            Voltage at x=0
        V_L: Optional
            Voltage at x=L
        I_0: Optional
            Current at x=0 (positive direction is from x=0 to x=L)
        I_L: Optional
            Current at x=L (positive direction is from x=0 to x=L)
        """
        self.beta = beta
        self.L = L
        self.Z0 = Z0
        
        # initialize by boundary conditions
        if 'V_plus' in kwargs and 'V_minus' in kwargs:
            self.V_plus = kwargs['V_plus']
            self.V_minus = kwargs['V_minus']
        elif 'V_0' in kwargs and 'V_L' in kwargs:
            self.V_plus, self.V_minus = self._V_pm_by_V0_VL(kwargs['V_0'], kwargs['V_L'])
        elif 'V_0' in kwargs and 'I_0' in kwargs:
            self.V_plus, self.V_minus = self._V_pm_by_V0_I0(kwargs['V_0'], kwargs['I_0'])
        elif 'V_L' in kwargs and 'I_L' in kwargs:
            self.V_plus, self.V_minus = self._V_pm_by_VL_IL(kwargs['V_L'], kwargs['I_L'])
        else:
            raise ValueError("Invalid boundary conditions: " + str(kwargs))
            
    def _ABCD_matrix(self) -> np.ndarray:
        """
        ABCD matrix of the transmission line, defined as
        [V0] = [A B] [VL]
        [I0]   [C D] [IL]
        where V0 and I0 are the voltage and current at x=0, 
        and VL and IL are the voltage and current at x=L.
        
        Note that both I0 and IL are positive when the current flows from x=0 to x=L.
        """
        if self.Z0 is None:
            raise ValueError("Z0 is not set")
        sin_bL = np.sin(self.beta * self.L)
        cos_bL = np.cos(self.beta * self.L)
        return np.array([
            [cos_bL, 1j * self.Z0 * sin_bL],
            [1j * sin_bL / self.Z0, cos_bL]
        ])
        
    def _V_pm_by_V0_VL(self, V_0: complex, V_L: complex) -> tuple[complex, complex]:
        e_jbL = np.exp(1j * self.beta * self.L)
        sin_bL = np.sin(self.beta * self.L)
        V_plus = (V_0 * e_jbL - V_L) / 2j / sin_bL
        V_minus = (V_L - V_0 / e_jbL) / 2j / sin_bL
        return V_plus, V_minus
    
    def _V_pm_by_V0_I0(self, V_0: complex, I_0: complex) -> tuple[complex, complex]:
        if self.Z0 is None:
            raise ValueError("Z0 is not set")
        VI_0 = np.array([[V_0], [I_0]])
        ABCD = self._ABCD_matrix()
        VI_L = np.linalg.inv(ABCD) @ VI_0
        V_L = VI_L[0, 0]
        return self._V_pm_by_V0_VL(V_0, V_L)
    
    def _V_pm_by_VL_IL(self, V_L: complex, I_L: complex) -> tuple[complex, complex]:
        if self.Z0 is None:
            raise ValueError("Z0 is not set")
        VI_L = np.array([[V_L], [I_L]])
        ABCD = self._ABCD_matrix()
        VI_0 = ABCD @ VI_L
        V_0 = VI_0[0, 0]
        return self._V_pm_by_V0_VL(V_0, V_L)

    def V(self, x):
        return (
            self.V_plus * np.exp(-1j * self.beta * x) + 
            self.V_minus * np.exp(+1j * self.beta * x)
        )
    
    def I(self, x):
        if self.Z0 is None:
            raise ValueError("Z0 is not set")
        return (
            self.V_plus * np.exp(-1j * self.beta * x) 
            - self.V_minus * np.exp(+1j * self.beta * x)
        ) / self.Z0
    
    def plot_V(self, ax):
        x = np.linspace(0, self.L, 100)
        ax.plot(x, self.V(x).real, label="Real")
        ax.plot(x, self.V(x).imag, label="Imag")
        ax.set_xlabel("x")
        ax.set_ylabel("V")
        ax.legend()
        ax.grid()
        return ax