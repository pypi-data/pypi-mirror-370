from .species import Species
from ..quantities import *


class CO(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=298)
        self.max_temp = Temperature(K=1300)
        self.Hf298 = Energy(kJmol=-110.53)
        self.thermo_params = {
            "A": 25.56759,
            "B": 6.096130,
            "C": 4.054656,
            "D": -2.671301,
            "E": 0.131021,
            "F": -118.0089,
            "G": 227.3665,
            "H": -110.5271,
        }
        super().__init__(T)
