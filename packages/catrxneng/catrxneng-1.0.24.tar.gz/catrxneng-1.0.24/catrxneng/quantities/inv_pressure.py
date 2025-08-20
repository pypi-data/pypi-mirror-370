from .quantity import Quantity
from catrxneng.utils import *


class InversePressure(Quantity):

    @property
    def inv_Pa(self):
        return self.si

    @inv_Pa.setter
    def inv_Pa(self, value):
        self.si = to_float(value)

    @property
    def inv_bar(self):
        return self.si * 100000

    @inv_bar.setter
    def inv_bar(self, value):
        self.si = to_float(value) / 100000

    @property
    def inv_kPa(self):
        return self.si * 1000 

    @inv_kPa.setter
    def inv_kPa(self, value):
        self.si = to_float(value) / 1000

    @property
    def inv_atm(self):
        return self.si * 101325 

    @inv_atm.setter
    def inv_atm(self, value):
        self.si = to_float(value) / 101325

    @property
    def inv_MPa(self):
        return self.si * 1000000 

    @inv_MPa.setter
    def inv_MPa(self, value):
        self.si = to_float(value) / 1000000