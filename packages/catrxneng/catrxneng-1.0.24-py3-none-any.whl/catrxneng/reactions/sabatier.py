from scipy.optimize import minimize, fsolve 
from .reaction import Reaction
from ..species import CO2, H2, CH4, H2O


class Sabatier(Reaction):
    def __init__(self, T):
        self.T = T
        self.components = {
            "CO2": CO2(T=T, stoich_coeff=-1),
            "H2": H2(T=T, stoich_coeff=-4),
            "CH4": CH4(T=T, stoich_coeff=1),
            "H2O": H2O(T=T, stoich_coeff=2),
        }
