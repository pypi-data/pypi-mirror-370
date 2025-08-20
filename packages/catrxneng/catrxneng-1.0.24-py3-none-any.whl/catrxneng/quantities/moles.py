from .quantity import Quantity
from catrxneng.utils import to_float


class Moles(Quantity):

    @property
    def mol(self):
        return self.si

    @mol.setter
    def mol(self, value):
        self.si = to_float(value)

    