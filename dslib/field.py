import math

from dslib import normalize_dash


class Field():

    def __init__(self, symbol: str, min, typ, max, mul=1, cond=None, unit=None):
        self.symbol = symbol

        if unit in {'uC', 'μC'}:
            assert mul == 1
            mul = 1000
            unit = 'nC'

        self.min = parse_field_value(min) * mul
        self.typ = parse_field_value(typ) * mul
        self.max = parse_field_value(max) * mul

        self.unit = unit

        self.cond = cond

        assert not math.isnan(self.typ) or not math.isnan(self.min) or not math.isnan(
            self.max), 'all nan ' + self.__repr__()

    def __repr__(self):
        return f'Field("{self.symbol}", min={self.min}, typ={self.typ}, max={self.max}, unit="{self.unit}", cond={repr(self.cond)})'

    @property
    def typ_or_max_or_min(self):
        if not math.isnan(self.typ):
            return self.typ
        elif not math.isnan(self.max):
            return self.max
        elif not math.isnan(self.min):
            return self.min
        raise ValueError()


def parse_field_value(s):
    if isinstance(s, (float, int)):
        return s
    if not s:
        return math.nan
    s = normalize_dash(s.strip().strip('\x03').rstrip('L'))
    if not s or s == '-' or set(s) == {'-'}:
        return math.nan
    return float(s)
