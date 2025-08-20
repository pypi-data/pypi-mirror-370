from .species import Species
from ..quantities import *

class CH4(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=298)
        self.max_temp = Temperature(K=1300)
        self.Hf298 = Energy(kJmol=-74.6)
        self.thermo_params = {
            "A": -0.703029,
            "B": 108.4773,
            "C": -42.52157,
            "D": 5.862788,
            "E": 0.678565,
            "F": -76.84376,
            "G": 158.7163,
            "H": -74.87310
        }
        super().__init__(T)
