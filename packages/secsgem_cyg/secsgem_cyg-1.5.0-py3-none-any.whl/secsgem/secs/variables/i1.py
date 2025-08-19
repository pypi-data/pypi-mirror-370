"""SECS 1 byte signed integer variable type."""

from .base_number import BaseNumber


class I1(BaseNumber):
    """Secs type for 1 byte signed data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o31
    text_code = "I1"
    _base_type = int
    _min = -128
    _max = 127
    _bytes = 1
    _struct_code = "b"
    preferred_types = [int]
