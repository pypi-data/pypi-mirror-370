from datetime import datetime, timezone
import pytz

time_format = "%Y-%m-%d_%H%M"
date_format = "%Y-%m-%d"


class Time:

    def __init__(self, **kwargs):
        if kwargs:
            setattr(self, list(kwargs.keys())[0], list(kwargs.values())[0])
        else:
            self.UET = int(datetime.now(timezone.utc).timestamp())

    @property
    def UTC(self):
        return datetime.fromtimestamp(self.UET, tz=pytz.utc)

    @UTC.setter
    def UTC(self, value):
        self.UET = int(value.timestamp())

    @property
    def ET(self):
        return self.UTC.astimezone(pytz.timezone("US/Eastern"))

    @ET.setter
    def ET(self, value):
        self.UET = int(value.timestamp())

    @property
    def iso(self):
        return datetime.fromtimestamp(self.UET, tz=timezone.utc).isoformat()

    @iso.setter
    def iso(self, value):
        dt = datetime.fromisoformat(value)
        self.UET = int(dt.timestamp())

    @property
    def UTC_str(self):
        return self.UTC.strftime("%Y-%m-%d_%H%M")

    @UTC_str.setter
    def UTC_str(self, value):
        tz = pytz.timezone("UTC")
        utc = datetime.strptime(value, "%Y-%m-%d_%H%M").astimezone(tz)
        self.UET = int(utc.timestamp())

    @property
    def ET_str(self):
        return self.ET.strftime("%Y-%m-%d_%H%M")

    @ET_str.setter
    def ET_str(self, value):
        tz = pytz.timezone("US/Eastern")
        et = datetime.strptime(value, "%Y-%m-%d_%H%M").astimezone(tz)
        self.UET = int(et.timestamp())

    @property
    def date_str(self):
        return self.ET.strftime("%Y-%m-%d")

    @date_str.setter
    def date_str(self, value):
        tz = pytz.timezone("US/Eastern")
        dt = datetime.strptime(value, "%Y-%m-%d")
        dt = tz.localize(dt)
        self.UET = int(dt.timestamp())

    @property
    def ET_disp(self):
        return self.ET.strftime("%Y-%m-%d %H:%M")

    def __sub__(self, other):
        if isinstance(other, Time):
            return Time(UET=self.UET - other.UET)
        if isinstance(other, (float, int)):
            return Time(UET=self.UET - other)
        raise ValueError("'other' must be Time, float, or int.")

    def __rsub__(self, other):
        if isinstance(other, Time):
            return Time(UET=other.UET - self.UET)
        raise ValueError("'other' must be Time.")

    def __add__(self, other):
        if isinstance(other, (float, int)):
            return Time(UET=int(self.UET + other))
        if isinstance(other, Time):
            return Time(UET=self.UET + other.UET)
        raise ValueError("'other' must be Time, float, or int.")

    def __radd__(self, other):
        if isinstance(other, Time):
            return Time(UET=other.UET + self.UET)
        raise ValueError("'other' must be Time.")

    def __gt__(self, other):
        if isinstance(other, Time):
            return self.UET > other.UET
        return TypeError("'other' must be an instance of Time.")

    def __rgt__(self, other):
        if isinstance(other, Time):
            return other.UET > self.UET
        return TypeError("'other' must be an instance of Time.")

    def __lt__(self, other):
        if isinstance(other, Time):
            return self.UET < other.UET
        return TypeError("'other' must be an instance of Time.")

    def __rlt__(self, other):
        if isinstance(other, Time):
            return other.UET < self.UET
        return TypeError("'other' must be an instance of Time.")
