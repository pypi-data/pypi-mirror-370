import numpy as np

from ..quantities import *


class Species:

    def __init__(self, T):
        self.T = T
        self.update()

    def update(self):
        self.check_temps()
        t = self.T / 1000
        params = self.thermo_params

        dHf = (
            params["A"] * t
            + params["B"] * t**2 / 2
            + params["C"] * t**3 / 3
            + params["D"] * t**4 / 4
            - params["E"] / t
            + params["F"]
            - params["H"]
        )  # kJ/mol
        self.Hf = Energy(kJmol=dHf.si) + self.Hf298

        Sf = (
            params["A"] * np.log(t)
            + params["B"] * t
            + params["C"] * t**2 / 2
            + params["D"] * t**3 / 3
            - params["E"] / (2 * t**2)
            + params["G"]
        ) / 1000  # kJ/mol/K
        self.Sf = Entropy(kJmolK=Sf.si)

        self.Gf = self.Hf + self.T * self.Sf

    def check_temps(self):
        if isinstance(self.T.si, np.ndarray):
            if self.T.si.min() < self.min_temp.si or self.T.si.max() > self.max_temp.si:
                raise ValueError("Temperature out of range for NIST parameters.")
        else:
            if self.T.si < self.min_temp.si or self.T.si > self.max_temp.si:
                raise ValueError("Temperature out of range for NIST parameters.")
