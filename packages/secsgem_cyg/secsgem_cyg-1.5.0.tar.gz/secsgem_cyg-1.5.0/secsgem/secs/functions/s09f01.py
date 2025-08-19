"""Class for stream 09 function 01."""

from secsgem.secs.data_items import MHEAD
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS09F01(SecsStreamFunction):
    """unrecognized device id.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F01
        MHEAD: B[10]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F01("HEADERDATA")
        S9F1
          <B 0x48 0x45 0x41 0x44 0x45 0x52 0x44 0x41 0x54 0x41> .

    Data Items:
        - :class:`MHEAD <secsgem.secs.data_items.MHEAD>`

    """

    _stream = 9
    _function = 1

    _data_format = MHEAD

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
