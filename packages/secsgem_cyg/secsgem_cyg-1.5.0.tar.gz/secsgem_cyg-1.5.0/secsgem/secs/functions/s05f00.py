"""Class for stream 05 function 00."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F00(SecsStreamFunction):
    """abort transaction stream 5.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F00
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F00()
        S5F0 .

    """

    _stream = 5
    _function = 0

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
