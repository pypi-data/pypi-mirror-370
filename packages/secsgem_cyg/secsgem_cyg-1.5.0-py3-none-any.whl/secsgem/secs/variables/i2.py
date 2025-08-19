"""SECS 2 byte signed integer variable type."""

from .base_number import BaseNumber


class I2(BaseNumber):
    """Secs type for 2 byte signed data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o32
    text_code = "I2"
    _base_type = int
    _min = -32768
    _max = 32767
    _bytes = 2
    _struct_code = "h"
    preferred_types = [int]
