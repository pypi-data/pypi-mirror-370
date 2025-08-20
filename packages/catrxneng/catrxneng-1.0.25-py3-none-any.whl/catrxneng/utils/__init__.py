import numpy as np, pandas as pd

from .influx import Influx
from .time import Time


def get_keys(obj1, obj2):
    if getattr(obj1, "keys", None) == getattr(obj2, "keys", None):
        keys = getattr(obj1, "keys", None)
    if getattr(obj1, "keys", None) is not None:
        keys = obj1.keys
    if getattr(obj2, "keys", None) is not None:
        keys = obj2.keys
    try:
        if keys is None:
            return None
        else:
            return keys.copy()
    except NameError:
        raise ValueError("Quantities have mismatching keys.")


def rate_const(T, Ea, k0=None, kref=None, Tref=None):
    from ..quantities import R, RateConstant

    if kref and Tref:
        k0 = kref / (np.exp(-Ea / (R * Tref)))
        k0 = RateConstant(si=k0.si, order=kref.order)

    k = k0 * np.exp(-Ea / (R * T))
    return RateConstant(si=k.si, order=k0.order)


def to_float(value):
    if isinstance(value, (np.ndarray, pd.Series)):
        return value.astype(float)
    if isinstance(value, int):
        return float(value)
    return value


def plot_info_box(text):
    text = text.replace("\\n", "\n")
    text = text.strip("\n")
    text = text.replace("\n", "<br>")
    annotations = [
        dict(
            x=0.5,
            y=-0.35,
            xref="paper",
            yref="paper",
            text=text,
            showarrow=False,
            font=dict(size=12, style="italic", weight="bold"),
        )
    ]
    return annotations


def divide(x, y):
    if isinstance(y, (np.ndarray, pd.Series)):
        y_safe = y.copy()
        y_safe[y_safe == 0] = np.nan
    else:
        y_safe = np.nan if y == 0 else y

    return x / y_safe


# def get_conf(conf_name):
#     conf_name = conf_name + ".conf"
#     conf_dir = os.path.join(os.path.dirname(__file__), "..", "..", "confs")
#     file_path = os.path.join(conf_dir, conf_name)
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(
#             f"Configuration file '{conf_name}' not found in 'conf' folder."
#         )
#     with open(file_path, "r") as file:
#         return json.load(file)
