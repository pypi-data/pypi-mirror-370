"""SECS 2 byte unsigned integer variable type."""

from .base_number import BaseNumber


class U2(BaseNumber):
    """Secs type for 2 byte unsigned data.

    :param value: initial value
    :type value: list/integer
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o52
    text_code = "U2"
    _base_type = int
    _min = 0
    _max = 65535
    _bytes = 2
    _struct_code = "H"
    preferred_types = [int]
