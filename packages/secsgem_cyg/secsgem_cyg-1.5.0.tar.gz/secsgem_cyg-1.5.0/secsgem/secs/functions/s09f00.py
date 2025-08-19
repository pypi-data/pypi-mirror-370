"""Class for stream 09 function 00."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS09F00(SecsStreamFunction):
    """abort transaction stream 9.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F00
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F00()
        S9F0 .

    """

    _stream = 9
    _function = 0

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
