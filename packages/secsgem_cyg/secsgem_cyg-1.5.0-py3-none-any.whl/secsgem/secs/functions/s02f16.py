"""Class for stream 02 function 16."""

from secsgem.secs.data_items import EAC
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F16(SecsStreamFunction):
    """new equipment constant - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F16
        EAC: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F16(secsgem.secs.data_items.EAC.BUSY)
        S2F16
          <B 0x2> .

    Data Items:
        - :class:`EAC <secsgem.secs.data_items.EAC>`

    """

    _stream = 2
    _function = 16

    _data_format = EAC

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
