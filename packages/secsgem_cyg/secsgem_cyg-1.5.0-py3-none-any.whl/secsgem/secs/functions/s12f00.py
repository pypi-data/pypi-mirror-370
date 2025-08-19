"""Class for stream 12 function 00."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F00(SecsStreamFunction):
    """abort transaction stream 12.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F00
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F00()
        S12F0 .

    """

    _stream = 12
    _function = 0

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
