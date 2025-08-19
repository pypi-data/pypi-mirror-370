"""Class for stream 01 function 15."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F15(SecsStreamFunction):
    """request offline.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F15
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F15()
        S1F15 W .

    """

    _stream = 1
    _function = 15

    _data_format = None

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
