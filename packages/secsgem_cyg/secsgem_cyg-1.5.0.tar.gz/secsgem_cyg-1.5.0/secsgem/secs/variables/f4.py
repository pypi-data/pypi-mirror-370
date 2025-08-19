"""SECS 4 byte float variable type."""

from .base_number import BaseNumber


class F4(BaseNumber):
    """Secs type for 4 byte float data.

    :param value: initial value
    :type value: list/float
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o44
    text_code = "F4"
    _base_type = float
    _min = -3.40282e+38
    _max = 3.40282e+38
    _bytes = 4
    _struct_code = "f"
    preferred_types = [float]
