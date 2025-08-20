from .reaction import Reaction
from ..quantities import *
from ..species import *


class RWGS(Reaction):
    def __init__(self, T, limiting_reactant="co2"):
        self.components = {
            "co2": CO2(T=T),
            "h2": H2(T=T),
            "co": CO(T=T),
            "h2o": H2O(T=T),
            "inert": Ar(T=T),
        }
        self.stoich_coeff = Unitless(
            si=[-1.0, -1.0, 1.0, 1.0, 0.0], keys=list(self.components.keys())
        )
        super().__init__(T, limiting_reactant)
