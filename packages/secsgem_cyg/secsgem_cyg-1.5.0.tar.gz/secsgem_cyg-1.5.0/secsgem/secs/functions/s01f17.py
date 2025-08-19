"""Class for stream 01 function 17."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F17(SecsStreamFunction):
    """request online.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F17
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F17()
        S1F17 W .

    """

    _stream = 1
    _function = 17

    _data_format = None

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
