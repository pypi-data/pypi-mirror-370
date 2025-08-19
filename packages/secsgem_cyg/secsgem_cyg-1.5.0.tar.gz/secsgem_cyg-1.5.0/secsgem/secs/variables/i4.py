"""SECS 4 byte signed integer variable type."""

from .base_number import BaseNumber


class I4(BaseNumber):
    """Secs type for 4 byte signed data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o34
    text_code = "I4"
    _base_type = int
    _min = -2147483648
    _max = 2147483647
    _bytes = 4
    _struct_code = "l"
    preferred_types = [int]
