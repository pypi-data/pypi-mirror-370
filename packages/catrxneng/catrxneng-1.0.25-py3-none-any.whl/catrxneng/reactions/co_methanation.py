from scipy.optimize import fsolve
from .reaction import Reaction
from ..species import CO, H2, CH4, H2O


class COMethanation(Reaction):
    def __init__(self, T):
        self.T = T
        self.components = {
            "CO": CO(T=T, stoich_coeff=-1),
            "H2": H2(T=T, stoich_coeff=-3),
            "CH4": CH4(T=T, stoich_coeff=1),
            "H2O": H2O(T=T, stoich_coeff=2),
        }

