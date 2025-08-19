"""SECS jis8 text variable type."""

import unicodedata

import secsgem.common.codec_jis_x_0201  # noqa: F401 pylint: disable=unused-import

from .base_text import BaseText


class JIS8(BaseText):
    """Secs type for string data.

    :param value: initial value
    :type value: string
    :param count: number of items this value
    :type count: integer
    """

    format_code = 0o21
    text_code = "J"
    preferred_types = [bytes, str]
    control_chars = "".join(chr(ch) for ch in range(256) if unicodedata.category(chr(ch))[0] == "C")
    coding = "jis_8"
