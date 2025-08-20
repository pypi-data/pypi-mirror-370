from .quantity import Quantity
from catrxneng.utils import *


class Mass(Quantity):

    @property
    def kg(self):
        return self.si

    @kg.setter
    def kg(self, value):
        self.si = to_float(value)

    @property
    def g(self):
        return self.si * 1000

    @g.setter
    def g(self, value):
        self.si = to_float(value) / 1000

    def __mul__(self, other):
        from .ghsv import GHSV 
        from .molar_flow_rate import MolarFlowRate
        from .reaction_rate import ReactionRate

        if isinstance(other, (GHSV, ReactionRate)):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__mul__(other)

    def __rmul__(self, other):
        from .ghsv import GHSV 
        from .molar_flow_rate import MolarFlowRate
        from .reaction_rate import ReactionRate

        if isinstance(other, (GHSV, ReactionRate)):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__rmul__(other)
