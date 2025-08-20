from .species import Species
from ..quantities import *


class CO2(Species):
    def __init__(self, T, stoich_coeff=None):
        self.min_temp = Temperature(K=298)
        self.max_temp = Temperature(K=1200)
        self.Hf298 = Energy(kJmol=-393.51)
        self.thermo_params = {
            "A": 24.99735,
            "B": 55.18696,
            "C": -33.69137,
            "D": 7.948387,
            "E": -0.136638,
            "F": -403.6075,
            "G": 228.2431,
            "H": -393.5224,
        }
        super().__init__(T)
