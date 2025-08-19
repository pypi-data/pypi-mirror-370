"""SECS 8 byte float variable type."""

from .base_number import BaseNumber


class F8(BaseNumber):
    """Secs type for 8 byte float data.

    :param value: initial value
    :type value: list/float
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o40
    text_code = "F8"
    _base_type = float
    _min = -1.79769e+308
    _max = 1.79769e+308
    _bytes = 8
    _struct_code = "d"
    preferred_types = [float]
