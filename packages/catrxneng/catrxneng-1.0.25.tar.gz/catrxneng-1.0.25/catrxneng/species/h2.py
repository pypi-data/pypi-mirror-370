from .species import Species
from ..quantities import *

class H2(Species):
    def __init__(self, T):
        self.min_temp = Temperature(K=298)
        self.max_temp = Temperature(K=1000)
        self.Hf298 =  Energy(kJmol=0)
        self.thermo_params = {
            "A": 33.066178,
            "B": -11.363417,
            "C": 11.432816,
            "D": -2.772874,
            "E": -0.158558,
            "F": -9.980797,
            "G": 172.707974,
            "H": 0,
        }
        super().__init__(T)
