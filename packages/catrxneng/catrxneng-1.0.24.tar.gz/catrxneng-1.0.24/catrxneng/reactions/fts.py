import numpy as np

from .reaction import Reaction
from ..quantities import *
from ..species import CO, H2, C2H4, H2O, Ar


class FTS(Reaction):
    def __init__(self, T):
        # self.components = {
        #     "CO": CO(T=T, stoich_coeff=-2),
        #     "H2": H2(T=T, stoich_coeff=-4),
        #     "C2H4": C2H4(T=T, stoich_coeff=1),
        #     "H2O": H2O(T=T, stoich_coeff=2),
        #     "inert": Ar(T=T, stoich_coeff=0)
        # }
        self.components = (CO(T), H2(T), C2H4(T), H2O(T), Ar(T))
        self.stoich_coeff = Unitless(si=[-2., -4., 1., 2., 0.])
        super().__init__(T)
