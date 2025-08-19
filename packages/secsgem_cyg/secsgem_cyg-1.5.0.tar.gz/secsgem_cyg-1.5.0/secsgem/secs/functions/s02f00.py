"""Class for stream 02 function 00."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F00(SecsStreamFunction):
    """abort transaction stream 2.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F00
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F00()
        S2F0 .

    """

    _stream = 2
    _function = 0

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
