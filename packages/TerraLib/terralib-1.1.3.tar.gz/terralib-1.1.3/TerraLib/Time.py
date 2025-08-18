# coding=utf-8
import decimal
import datetime
import re
from decimal import Decimal


def timestamp_to_time(timestamp):
    try:
        timestamp = float(timestamp)
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        print(f"[WARN]Can not convert [{timestamp}] to time str!")
        return timestamp


def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Time():
    def __init__(self, time):
        t = str(time).lower().replace(" ", "").strip()
        s_mo = re.match(r"^([+-]?[\d.]+)s?$", t)
        ms_mo = re.match(r"^([+-]?[\d.]+)ms?$", t)
        us_mo = re.match(r"^([+-]?[\d.]+)us?$", t)
        ns_mo = re.match(r"^([+-]?[\d.]+)ns?$", t)
        ps_mo = re.match(r"^([+-]?[\d.]+)ps?$", t)
        fs_mo = re.match(r"^([+-]?[\d.]+)fs?$", t)

        if s_mo:
            self.value = Decimal(s_mo.group(1))
            self.unit = "s"
        elif ms_mo:
            self.value = Decimal(ms_mo.group(1))
            self.unit = "ms"
        elif us_mo:
            self.value = Decimal(us_mo.group(1))
            self.unit = "us"
        elif ns_mo:
            self.value = Decimal(ns_mo.group(1))
            self.unit = "ns"
        elif ps_mo:
            self.value = Decimal(ps_mo.group(1))
            self.unit = "ps"
        elif fs_mo:
            self.value = Decimal(fs_mo.group(1))
            self.unit = "fs"
        else:
            raise ValueError(f"Can not accept the format for {time}!")

    def trans(self, unit):
        units = ["s", "ms", "us", "ns", "ps", "fs"]
        if unit not in units:
            raise ValueError(f"Your unit [{unit}] is not support.")
        self_idx = units.index(self.unit)
        target_idx = units.index(unit)
        delta = target_idx - self_idx
        self.value = self.value * decimal.ExtendedContext.power(1000, delta)
        self.unit = unit
        return self

    def __repr__(self):
        return f"{self.value}{self.unit}"

    def __add__(self, other):
        other = other.trans(self.unit)
        return Time(f"{self.value + other.value}{self.unit}")

    def __sub__(self, other):
        other = other.trans(self.unit)
        return Time(f"{self.value - other.value}{self.unit}")

    def __lt__(self, other):
        other = other.trans(self.unit)
        return self.value.__lt__(other.value)

    def __le__(self, other):
        other = other.trans(self.unit)
        return self.value.__le__(other.value)

    def __gt__(self, other):
        other = other.trans(self.unit)
        return self.value.__gt__(other.value)

    def __ge__(self, other):
        other = other.trans(self.unit)
        return self.value.__ge__(other.value)

    def __eq__(self, other):
        other = other.trans(self.unit)
        return self.value.__eq__(other.value)
