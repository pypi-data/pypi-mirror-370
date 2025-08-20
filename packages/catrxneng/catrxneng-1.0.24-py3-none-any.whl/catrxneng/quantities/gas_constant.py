from .quantity import Quantity
from .temperature import Temperature
from .energy import Energy


class GasConstant(Quantity):

    @property
    def si(self):
        return 8.314

    @property
    def JmolK(self):
        return self.si

    @property
    def m3PaKmol(self):
        return self.si

    @property
    def kJmolK(self):
        return 0.008314

    @property
    def LbarKmol(self):
        return 0.08314
    
    def __mul__(self, other):
        if isinstance(other, Temperature):
            si = self.si * other.si
            return Energy(si=si)
        return super().__mul__(other)

    def __rmul__(self, other):
        if isinstance(other, Temperature):
            si = other.si * self.si 
            return Energy(si=si)
        return super().__rmul__(other)
