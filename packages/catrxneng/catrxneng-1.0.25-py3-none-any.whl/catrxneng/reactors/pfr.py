import numpy as np
from scipy.integrate import solve_ivp

from .. import utils
from ..quantities import *
from .reactor import Reactor


class PFR(Reactor):
    def __init__(self, rate_model, T, p0, ghsv, mcat, limiting_reactant):
        self.rate_model = rate_model
        self.T = T
        self.p0 = p0
        self.ghsv = ghsv
        self.mcat = mcat
        self.limiting_reactant = limiting_reactant
        self.Ft0 = ghsv * mcat
        self.P = np.sum(p0)
        self.y0 = utils.divide(p0, self.P)
        self.F0 = self.y0 * self.Ft0
        # self.F = self.F0
        # self.extent = Moles(si=0)
        # self.conversion = Unitless(si=0)
        self.check_components()

    def dFdw(self, w, F):
        F = MolarFlowRate(molh=F)
        Ft = np.sum(F)
        y = F / Ft
        p = y * self.P
        return np.array(
            [rate(self.T, p).molhgcat for rate in self.rate_model.rate.values()]
        )

    def solve(self):
        w_span = (0, self.mcat.g)
        w_eval = np.linspace(0, self.mcat.g, 1000)
        solution = solve_ivp(self.dFdw, w_span, self.F0.molh, t_eval=w_eval)
        self.w = Mass(g=solution.t)
        self.F = MolarFlowRate(molh=solution.y, keys=self.rate_model.components.copy())
        self.conversion = utils.divide(
            self.F0[self.limiting_reactant] - self.F[self.limiting_reactant],
            self.F0[self.limiting_reactant],
        )
        self.inv_ghsv = InvGHSV(si=self.w.si / self.Ft0.si)
        self.ghsv = GHSV(si=utils.divide(1, self.inv_ghsv.si))
        vol_flow_rate = self.Ft0.si * R.si * self.T.si / self.P.si
        self.vol_flow_rate = VolumetricFlowRate(si=vol_flow_rate)
        self.tau_mod = Quantity(si=self.w.g / self.vol_flow_rate.mLs)

    @property
    def Ft(self):
        return np.sum(self.F, axis=0)

    # def rate(self):
    #     p = self.y * self.P
    #     rates = []
    #     for ri in self.rate_model.rate:
    #         rates.append(ri(self.T, p))
    #     return rates
