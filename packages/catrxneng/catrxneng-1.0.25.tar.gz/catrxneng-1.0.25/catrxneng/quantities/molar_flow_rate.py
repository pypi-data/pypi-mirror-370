from .quantity import Quantity
from catrxneng.utils import *


class MolarFlowRate(Quantity):

    @property
    def mols(self):
        return self.si

    @mols.setter
    def mols(self, value):
        self.si = to_float(value)

    @property
    def molmin(self):
        return self.si * 60

    @molmin.setter
    def molmin(self, value):
        self.si = to_float(value / 60)

    @property
    def molh(self):
        return self.si * 3600

    @molh.setter
    def molh(self, value):
        self.si = to_float(value / 3600)

    @property
    def smLmin(self):
        return self.si * 60 * 22.4 * 1000

    @smLmin.setter
    def smLmin(self, value):
        self.si = to_float(value / 60 / 22.4 / 1000)

    @property
    def nmLmin(self):
        return self.si * 60 * 24.05 * 1000

    @nmLmin.setter
    def nmLmin(self, value):
        self.si = to_float(value / 60 / 24.05 / 1000)
    