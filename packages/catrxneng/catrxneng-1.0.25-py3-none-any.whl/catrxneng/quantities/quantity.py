import numpy as np
from catrxneng import utils


class Quantity:
    def __init__(self, **kwargs):
        if kwargs:
            try:
                key = list(kwargs.keys())[0]
                value = list(kwargs.values())[0]
                if isinstance(value, (list, tuple)):
                    value = np.array(value)
                if isinstance(value, dict):
                    self.keys = list(value.keys())
                    value = np.array(list(value.values()))
                setattr(self, key, value)
            except:
                raise ValueError("Invalid arguments.")
            if not hasattr(self, "keys"):
                self.keys = kwargs.get("keys")

    @property
    def initial(self):
        if isinstance(self.si, np.ndarray):
            return type(self)(si=[col[0] for col in self.si])
        return type(self)(si=self.si[0])

    @property
    def final(self):
        if isinstance(self.si, np.ndarray):
            return type(self)(si=[col[-1] for col in self.si])
        return type(self)(si=self.si[-1])

    @property
    def size(self):
        if isinstance(self.si, np.ndarray):
            return self.si.size
        return 1

    def __getitem__(self, index):
        if isinstance(index, str):
            try:
                index = self.keys.index(index)
            except AttributeError:
                raise KeyError("Key not found.")
        return type(self)(si=self.si[index])

    def __setitem__(self, key, value):
        if isinstance(value, Quantity):
            value = value.si
        if key in self.keys:
            index = self.keys.index(key)
            self.si[index] = value
        else:
            self.keys.append(key)
            self.si = np.append(self.si, value)

    def __add__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si + other.si
        return type(self)(si=si, keys=keys)

    def __radd__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si + self.si
        return type(self)(si=si, keys=keys)

    def __sub__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si - other.si
        return type(self)(si=si, keys=keys)

    def __rsub__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si - self.si
        return type(self)(si=si, keys=keys)

    def __mul__(self, other):
        from .unitless import Unitless

        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Unitless(si=other)
            # other = Quantity(si=other)
        si = self.si * other.si
        if isinstance(other, Unitless):
            return type(self)(si=si, keys=keys)
        if isinstance(self, Unitless):
            return type(other)(si=si, keys=keys)
        return Quantity(si=si, keys=keys)

    def __rmul__(self, other):
        from .unitless import Unitless

        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Unitless(si=other)
            # other = Quantity(si=other)
        si = other.si * self.si
        if isinstance(other, Unitless):
            return type(self)(si=si, keys=keys)
        if isinstance(self, Unitless):
            return type(other)(si=si, keys=keys)
        return Quantity(si=si, keys=keys)

    def __truediv__(self, other):
        from .unitless import Unitless

        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = utils.divide(self.si, other.si)
        if isinstance(other, Unitless):
            return type(self)(si=si, keys=keys)
        if type(other) is type(self) and not type(self) is Quantity:
            return Unitless(si=si, keys=keys)
        return Quantity(si=si, keys=keys)

    def __rtruediv__(self, other):
        from .unitless import Unitless

        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = np.divide(other.si, self.si)
        if isinstance(other, Unitless):
            return type(self)(si=si, keys=keys)
        if type(other) is type(self):
            return Unitless(si=si, keys=keys)
        return Quantity(si=si, keys=keys)

    def __pow__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si**other.si
        return Quantity(si=si, keys=keys)

    def __rpow__(self, other):
        keys = utils.get_keys(self, other)
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si**self.si
        return Quantity(si=si, keys=keys)

    def __neg__(self):
        return type(self)(si=-self.si, keys=self.keys)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        from .unitless import Unitless

        if ufunc == np.power:
            base, exp = inputs
            if isinstance(base, Quantity) and isinstance(exp, (int, float, np.ndarray)):
                return Quantity(si=np.power(base.si, exp), keys=base.keys)
            elif isinstance(exp, Quantity) and isinstance(
                base, (int, float, np.ndarray)
            ):
                return Quantity(si=np.power(base, exp.si), keys=exp.keys)
            elif isinstance(exp, Quantity) and isinstance(base, Quantity):
                keys = utils.get_keys(exp, base)
                return Quantity(si=np.power(base.si, exp.si), keys=keys)
            else:
                raise TypeError("Invalid types for np.power with Quantity.")
        elif ufunc == np.add and method == "reduce":
            si = ufunc.reduce(inputs[0].si, **kwargs)
            return type(self)(si=si, keys=self.keys)
        elif ufunc == np.multiply and method == "reduce":
            si = ufunc.reduce(inputs[0].si, **kwargs)
            return Quantity(si=si, keys=self.keys)
        elif ufunc == np.exp:
            si = ufunc(inputs[0].si)
            if isinstance(inputs[0], Unitless):
                return Unitless(si=si, keys=self.keys)
            return Quantity(si=si, keys=self.keys)
        elif ufunc == np.log:
            si = ufunc(inputs[0].si)
            if isinstance(inputs[0], Unitless):
                return Unitless(si=si, keys=self.keys)
            return Quantity(si=si, keys=self.keys)
        return NotImplemented
