"""Class for stream 09 function 09."""

from secsgem.secs.data_items import SHEAD
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS09F09(SecsStreamFunction):
    """transaction timer timeout.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F09
        SHEAD: B[10]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F09("HEADERDATA")
        S9F9
          <B 0x48 0x45 0x41 0x44 0x45 0x52 0x44 0x41 0x54 0x41> .

    Data Items:
        - :class:`SHEAD <secsgem.secs.data_items.SHEAD>`

    """

    _stream = 9
    _function = 9

    _data_format = SHEAD

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
