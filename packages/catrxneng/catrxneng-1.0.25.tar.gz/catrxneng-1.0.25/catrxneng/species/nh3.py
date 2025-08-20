from .species import Species
from ..quantities import *


class NH3(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=298) 
        self.max_temp = Temperature(K=1400)
        self.Hf298 =  Energy(kJmol=-45.9)
        self.thermo_params = {
            "A": 19.99563,
            "B": 49.77119,
            "C": -15.37599,
            "D": 1.921168,
            "E": 0.189174,
            "F": -53.30667,
            "G": 203.8591,
            "H": -45.89806,
        }
        super().__init__(T)

