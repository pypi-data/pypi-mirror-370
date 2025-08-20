from .quantity import Quantity
from catrxneng.utils import *


class InvGHSV(Quantity):

    @property
    def molskgcat(self):
        return self.si

    @molskgcat.setter
    def molskgcat(self, value):
        self.si = to_float(value)

    @property
    def smLhgcat(self):
        return self.si / 3600 / 22.4

    @smLhgcat.setter
    def smLhgcat(self, value):
        self.si = to_float(value) * 3600 * 22.4
