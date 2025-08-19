"""SECS 4 byte unsigned integer variable type."""

from .base_number import BaseNumber


class U4(BaseNumber):
    """Secs type for 4 byte unsigned data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o54
    text_code = "U4"
    _base_type = int
    _min = 0
    _max = 4294967295
    _bytes = 4
    _struct_code = "L"
    preferred_types = [int]
