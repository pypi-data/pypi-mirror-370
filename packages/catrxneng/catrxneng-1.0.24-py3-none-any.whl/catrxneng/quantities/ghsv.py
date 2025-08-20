from .quantity import Quantity
from catrxneng.utils import *


class GHSV(Quantity):

    @property
    def molskgcat(self):
        return self.si

    @molskgcat.setter
    def molskgcat(self, value):
        self.si = to_float(value)

    @property
    def smLhgcat(self):
        return self.si * 3600 * 22.4

    @smLhgcat.setter
    def smLhgcat(self, value):
        self.si = to_float(value) / 3600 / 22.4

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