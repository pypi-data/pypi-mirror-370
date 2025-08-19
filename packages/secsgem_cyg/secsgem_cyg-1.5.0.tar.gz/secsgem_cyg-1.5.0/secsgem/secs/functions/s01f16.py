"""Class for stream 01 function 16."""

from secsgem.secs.data_items import OFLACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F16(SecsStreamFunction):
    """offline acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F16
        OFLACK: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F16(secsgem.secs.data_items.OFLACK.ACK)
        S1F16
          <B 0x0> .

    Data Items:
        - :class:`OFLACK <secsgem.secs.data_items.OFLACK>`

    """

    _stream = 1
    _function = 16

    _data_format = OFLACK

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
