from .species import Species
from ..quantities import *


class Ar(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=500) 
        self.max_temp = Temperature(K=2000)
        self.Hf298 =  Energy(kJmol=0)
        self.thermo_params = {
            "A": 19.50583,
            "B": 19.88705,
            "C": -8.598535,
            "D": 1.369784,
            "E": 0.527601,
            "F": -4.935202,
            "G": 212.3900,
            "H": 0.0,
        }
        super().__init__(T)

