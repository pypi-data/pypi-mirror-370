"""SECS 8 byte signed integer variable type."""

from .base_number import BaseNumber


class I8(BaseNumber):
    """Secs type for 8 byte signed data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o30
    text_code = "I8"
    _base_type = int
    _min = -9223372036854775808
    _max = 9223372036854775807
    _bytes = 8
    _struct_code = "q"
    preferred_types = [int]
