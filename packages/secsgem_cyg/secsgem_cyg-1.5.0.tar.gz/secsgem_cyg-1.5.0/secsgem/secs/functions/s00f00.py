"""Class for stream 00 function 00."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS00F00(SecsStreamFunction):
    """Hsms communication.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS00F00
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS00F00()
        S0F0 .

    """

    _stream = 0
    _function = 0

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
