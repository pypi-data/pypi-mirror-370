from .reaction import Reaction
from .. import species
from ..quantities import Unitless


class AmmoniaSynthesis(Reaction):
    def __init__(self, T):
        self.components = {
            "N2": species.N2(T=T),
            "H2": species.H2(T=T),
            "NH3": species.NH3(T=T),
            "inert": species.Ar(T=T)
        }
        self.stoich_coeff = Unitless(si=[-0.5, -1.5, 1, 0])
        super().__init__(T)
