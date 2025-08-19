"""Class for stream 07 function 18."""

from secsgem.secs.data_items import ACKC7
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F18(SecsStreamFunction):
    """delete process program - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F18
        ACKC7: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F18(secsgem.secs.data_items.ACKC7.MODE_UNSUPPORTED)
        S7F18
          <B 0x5> .

    Data Items:
        - :class:`ACKC7 <secsgem.secs.data_items.ACKC7>`

    """

    _stream = 7
    _function = 18

    _data_format = ACKC7

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
