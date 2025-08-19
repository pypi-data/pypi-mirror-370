"""Class for stream 01 function 01."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F01(SecsStreamFunction):
    """are you online - request.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F01
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F01()
        S1F1 W .

    """

    _stream = 1
    _function = 1

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
