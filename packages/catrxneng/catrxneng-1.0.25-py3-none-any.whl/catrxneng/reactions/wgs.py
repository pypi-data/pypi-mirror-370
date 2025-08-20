from .reaction import Reaction
from .. import species


class WGS(Reaction):
    def __init__(self, T):
        self.components = {
            "CO": species.CO(T=T, stoich_coeff=-1),
            "H2O": species.H2O(T=T, stoich_coeff=-1),
            "CO2": species.CO2(T=T, stoich_coeff=1),
            "H2": species.H2(T=T, stoich_coeff=1),
            "inert": species.Ar(T=T, stoich_coeff=0)
        }
        super().__init__(T=T)