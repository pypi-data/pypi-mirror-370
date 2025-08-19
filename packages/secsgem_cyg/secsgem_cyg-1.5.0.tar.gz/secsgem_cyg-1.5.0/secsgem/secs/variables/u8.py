"""SECS 8 byte unsigned integer variable type."""

from .base_number import BaseNumber


class U8(BaseNumber):
    """Secs type for 8 byte unsigned data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o50
    text_code = "U8"
    _base_type = int
    _min = 0
    _max = 18446744073709551615
    _bytes = 8
    _struct_code = "Q"
    preferred_types = [int]
