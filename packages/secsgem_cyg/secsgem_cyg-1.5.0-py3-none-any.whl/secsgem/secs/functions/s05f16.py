"""Class for stream 05 function 16."""

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F16(SecsStreamFunction):
    """exception recover complete - confirm.

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F16
        Header only

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F16()
        S5F16 .

    """

    _stream = 5
    _function = 16

    _data_format = None

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
