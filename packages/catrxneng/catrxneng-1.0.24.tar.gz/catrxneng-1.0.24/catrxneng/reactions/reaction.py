import numpy as np
from scipy.optimize import minimize

from catrxneng.quantities import *


class Reaction:
    def __init__(self, T, limiting_reactant):
        self.T = T
        self.limiting_reactant = limiting_reactant
        self.fug_coeff = Unitless(
            si=np.ones(len(self.components)), keys=list(self.components.keys())
        )
        self.update()

    def update(self):
        for comp in self.components.values():
            comp.T = self.T
        self.Hf = Energy(si=[comp.Hf.si for comp in self.components.values()])
        self.Sf = Entropy(si=[comp.Sf.si for comp in self.components.values()])
        self.dHr = np.sum(self.Hf * self.stoich_coeff)
        self.dSr = np.sum(self.Sf * self.stoich_coeff)
        self.dGr = self.dHr - self.dSr * self.T
        self.Keq = np.exp(-self.dGr / (R * self.T))

    def check_components(self, p0):
        if p0.keys != list(self.components.keys):
            raise ValueError("Partial pressure keys do not match reaction components.")

    def equilibrate(self, p0):
        self.check_components(p0)
        P = np.sum(p0)
        initial_total_moles = Moles(si=100)
        initial_molfrac = p0 / P
        initial_moles = initial_molfrac * initial_total_moles
        std_state_fugacity = Pressure(atm=np.ones(len(self.components)))

        def objective(extent):

            extent = Moles(si=extent)
            moles = initial_moles + extent * self.stoich_coeff
            total_moles = np.sum(moles)
            molfrac = moles / total_moles
            fugacity = molfrac * self.fug_coeff * P
            activity = fugacity / std_state_fugacity
            Ka = np.prod(activity**self.stoich_coeff)
            # Kx = np.prod(molfrac**self.stoich_coeff)
            # Kphi = np.prod(self.fug_coeff**self.stoich_coeff)
            # Kp = np.prod(P**self.stoich_coeff)
            # Kf0 = np.prod(std_state_fugacity**self.stoich_coeff)
            return ((Ka - self.Keq) ** 2).si * 1e5

        adj_init_mol_reactants = np.array(
            [
                mol / stoich_coeff
                for mol, stoich_coeff in zip(initial_moles.si, self.stoich_coeff.si)
                if stoich_coeff < 0
            ]
        )
        min_extent = 1e-5
        bounds = [(min_extent, np.min(-adj_init_mol_reactants) * (1 - min_extent))]
        initial_guess = -0.5 * initial_moles.si[0] / self.stoich_coeff.si[0]
        result = minimize(
            objective,
            initial_guess,
            bounds=bounds,
            options={"ftol": 1e-10},
        )
        if result.success:
            self.extent = Moles(si=result.x[0])
            moles = initial_moles + self.extent * self.stoich_coeff
            self.conversion = (
                initial_moles[self.limiting_reactant] - moles[self.limiting_reactant]
            ) / initial_moles[self.limiting_reactant]
            total_moles = Moles(si=np.sum(moles.si))
            self.molfrac = moles / total_moles
        else:
            raise ValueError("Optimization failed: " + result.message)
