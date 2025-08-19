"""Class for stream 12 function 06."""

from secsgem.secs.data_items import GRNT1
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F06(SecsStreamFunction):
    """map transmit - grant.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F06
        GRNT1: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F06(secsgem.secs.data_items.GRNT1.MATERIALID_UNKNOWN)
        S12F6
          <B 0x5> .

    Data Items:
        - :class:`GRNT1 <secsgem.secs.data_items.GRNT1>`

    """

    _stream = 12
    _function = 6

    _data_format = GRNT1

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
