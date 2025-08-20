from .species import Species
from ..quantities import *


class C2H4(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=298)
        self.max_temp = Temperature(K=1200)
        self.Hf298 = Energy(kJmol=52.4)
        self.thermo_params = {
            "A": -6.387880,
            "B": 184.4019,
            "C": -112.9718,
            "D": 28.49593,
            "E": 0.315540,
            "F": 48.17332,
            "G": 163.1568,
            "H": 52.46694
        }
        super().__init__(T)
