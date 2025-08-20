from scipy.optimize import fsolve

from ..quantities import *
from .reaction import Reaction
from ..species import CO2, H2, C2H4, H2O, Ar


class CO2FTS(Reaction):
    def __init__(self, T):
        # self.components = {
        #     "CO2": CO2(T=T, stoich_coeff=-2),
        #     "H2": H2(T=T, stoich_coeff=-6),
        #     "C2H4": C2H4(T=T, stoich_coeff=1),
        #     "H2O": H2O(T=T, stoich_coeff=4),
        #     "inert": Ar(T=T, stoich_coeff=0)
        # }
        self.components = (CO2(T), H2(T), C2H4(T), H2O(T), Ar(T))
        self.stoich_coeff = Unitless(si=[-2., -6., 1., 4., 0.])
        super().__init__(T)
