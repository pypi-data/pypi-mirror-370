from .quantity import Quantity
from catrxneng.utils import *


class VolumetricFlowRate(Quantity):

    @property
    def m3s(self):
        return self.si

    @m3s.setter
    def m3s(self, value):
        self.si = to_float(value)

    @property
    def mLs(self):
        return self.si * 1000 * 1000

    @mLs.setter
    def mLs(self, value):
        self.si = to_float(value) / 1000 / 1000