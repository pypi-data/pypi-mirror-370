from .quantity import Quantity
from ..utils import *


class Energy(Quantity):

    @property
    def Jmol(self):
        return self.si

    @Jmol.setter
    def Jmol(self, value):
        self.si = to_float(value)

    @property
    def kJmol(self):
        return self.si / 1000

    @kJmol.setter
    def kJmol(self, value):
        self.si = to_float(value * 1000)

    @property
    def kcalmol(self):
        return self.si / 4184

    @kcalmol.setter
    def kcalmol(self, value):
        self.si = to_float(value * 4184)
