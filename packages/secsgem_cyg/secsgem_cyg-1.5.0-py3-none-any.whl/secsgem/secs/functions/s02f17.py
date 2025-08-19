"""Class for stream 02 function 17."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F17(SecsStreamFunction):
    """date and time - request.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F17
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F17()
        S2F17 W .

    """

    _stream = 2
    _function = 17

    _data_format = None

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
