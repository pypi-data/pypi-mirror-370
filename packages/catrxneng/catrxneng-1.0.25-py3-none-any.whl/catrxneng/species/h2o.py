from .species import Species
from ..quantities import *


class H2O(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=500)
        self.max_temp = Temperature(K=1700)
        self.Hf298 = Energy(kJmol=-241.83)
        self.thermo_params = {
            "A": 30.09200,
            "B": 6.832514,
            "C": 6.793435,
            "D": -2.534480,
            "E": 0.082139,
            "F": -250.8810,
            "G": 223.3967,
            "H": -241.8264
        }
        super().__init__(T)
