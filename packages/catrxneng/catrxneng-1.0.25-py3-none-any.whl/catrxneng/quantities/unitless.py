from .quantity import Quantity


class Unitless(Quantity):

    @property
    def pct(self):
        return self.si / 100
