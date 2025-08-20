from .quantity import Quantity
from catrxneng.utils import *


class Pressure(Quantity):

    @property
    def Pa(self):
        return self.si

    @Pa.setter
    def Pa(self, value):
        self.si = to_float(value)

    @property
    def bar(self):
        return self.si / 100000

    @bar.setter
    def bar(self, value):
        self.si = to_float(value) * 100000

    @property
    def kPa(self):
        return self.si / 1000 

    @kPa.setter
    def kPa(self, value):
        self.si = to_float(value) * 1000

    @property
    def atm(self):
        return self.si / 101325 

    @atm.setter
    def atm(self, value):
        self.si = to_float(value) * 101325

    @property
    def MPa(self):
        return self.si / 1000000 

    @MPa.setter
    def MPa(self, value):
        self.si = to_float(value) * 1000000