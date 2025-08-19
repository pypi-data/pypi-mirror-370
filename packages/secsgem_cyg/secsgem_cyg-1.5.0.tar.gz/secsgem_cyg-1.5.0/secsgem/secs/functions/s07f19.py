"""Class for stream 07 function 19."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F19(SecsStreamFunction):
    """current equipment process program - request.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F19
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F19()
        S7F19 W .

    """

    _stream = 7
    _function = 19

    _data_format = None

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
