"""Class for stream 05 function 17."""

from secsgem.secs.data_items import EXID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F17(SecsStreamFunction):
    """exception recover abort - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F17
        EXID: A[20]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F17("EX123")
        S5F17 W
          <A "EX123"> .

    Data Items:
        - :class:`EXID <secsgem.secs.data_items.EXID>`

    """

    _stream = 5
    _function = 17

    _data_format = EXID

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
