"""SECS 1 byte unsigned integer variable type."""

from .base_number import BaseNumber


class U1(BaseNumber):
    """Secs type for 1 byte unsigned data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o51
    text_code = "U1"
    _base_type = int
    _min = 0
    _max = 255
    _bytes = 1
    _struct_code = "B"
    preferred_types = [int]
