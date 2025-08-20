from .quantity import Quantity
from catrxneng.utils import *


class ReactionRate(Quantity):

    @property
    def molskgcat(self):
        return self.si

    @molskgcat.setter
    def molskgcat(self, value):
        self.si = to_float(value)

    @property
    def molhgcat(self):
        return self.si * 3600 / 1000

    @molhgcat.setter
    def molhgcat(self, value):
        self.si = to_float(value / 3600 * 1000)

    @property
    def mmolhgcat(self):
        return self.si * 3600 

    @mmolhgcat.setter
    def mmolhgcat(self, value):
        self.si = to_float(value / 3600)

    @property
    def molhkgcat(self):
        return self.si * 3600 

    @molhkgcat.setter
    def molhkgcat(self, value):
        self.si = to_float(value / 3600)

    def __mul__(self, other):
        from .mass import Mass
        from .molar_flow_rate import MolarFlowRate

        if isinstance(other, Mass):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__mul__(other)

    def __rmul__(self, other):
        from .mass import Mass
        from .molar_flow_rate import MolarFlowRate

        if isinstance(other, Mass):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__rmul__(other)