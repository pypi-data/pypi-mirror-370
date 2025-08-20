from catrxneng.utils import rate_const
from catrxneng.reactions import RWGS
from catrxneng.quantities import *


class Brubach2022:
    def __init__(self):
        self.components = ["co2", "h2", "co", "h2o", "inert"]
        self.Ea_rwgs = Energy(kJmol=115)
        self.Ea_ft = Energy(kJmol=67.8)
        self.a_rwgs = Unitless(si=16.3)
        self.a_ft = Unitless(si=9.07)
        self.b_ft = InversePressure(inv_bar=2.44)
        self.kref_rwgs = RateConstant(order=1.5, molhgcatbar=8.13e-2)
        self.kref_ft = RateConstant(order=2, molhgcatbar=6.39e-2)
        self.Tref = Temperature(C=300)

    def k_rwgs(self, T):
        return rate_const(T=T, Ea=self.Ea_rwgs, kref=self.kref_rwgs, Tref=self.Tref)

    def k_ft(self, T):
        return rate_const(T=T, Ea=self.Ea_ft, kref=self.kref_ft, Tref=self.Tref)

    def r_rwgs(self, T, p):
        fwd = p["co2"] * p["h2"] ** 0.5
        rev = p["co"] * p["h2o"] / (RWGS(T).Keq * p["h2"] ** 0.5)
        num = self.k_rwgs(T) * (fwd - rev)
        denom = (1 + self.a_rwgs * p["h2o"] / p["h2"]) ** 2
        rate = num / denom
        return ReactionRate(si=rate.si)

    def r_ft(self, T, p):
        num = self.k_ft(T) * p["h2"] * p["co"]
        denom = (1 + self.a_ft * p["h2o"] / p[1] + self.b_ft * p["co"]) ** 2
        rate = num / denom
        return ReactionRate(si=rate.si)

    @property
    def rate(self):
        return {
            "co2": lambda T, p: -self.r_rwgs(T, p),
            "h2": lambda T, p: -self.r_rwgs(T, p) - 2 * self.r_ft(T, p),
            "co": lambda T, p: self.r_rwgs(T, p) - self.r_ft(T, p),
            "h2o": lambda T, p: self.r_rwgs(T, p) + self.r_ft(T, p),
            "inert": lambda T, p: ReactionRate(si=0)
        }
