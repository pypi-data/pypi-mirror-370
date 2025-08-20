from .quantity import Quantity
from catrxneng.utils import *


class Temperature(Quantity):

    @property
    def K(self):
        return self.si

    @K.setter
    def K(self, value):
        self.si = to_float(value)

    @property
    def C(self):
        return self.si - 273

    @C.setter
    def C(self, value):
        self.si = to_float(value + 273)

    def __mul__(self, other):
        from .energy import Energy
        from .entropy import Entropy
        if isinstance(other, Entropy):
            si = self.si * other.si
            return Energy(si=si)
        else:
            return super().__mul__(other)

    def __rmul__(self, other):
        from .energy import Energy
        from .entropy import Entropy
        if isinstance(other, Entropy):
            si = other.si * self.si
            return Energy(si=si)
        else:
            return super().__rmul__(other)
