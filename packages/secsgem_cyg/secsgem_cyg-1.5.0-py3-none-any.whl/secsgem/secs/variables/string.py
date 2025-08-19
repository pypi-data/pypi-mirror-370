"""SECS string text variable type."""

import unicodedata

from .base_text import BaseText


class String(BaseText):
    """Secs type for string data.

    :param value: initial value
    :type value: string
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o20
    text_code = "A"
    preferred_types = [bytes, str]
    control_chars = "".join(chr(ch) for ch in range(256) if unicodedata.category(chr(ch))[0] == "C" or ch > 127)
    coding = "latin-1"
