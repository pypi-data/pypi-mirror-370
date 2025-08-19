"""Class for stream 02 function 38."""

from secsgem.secs.data_items import ERACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F38(SecsStreamFunction):
    """en-/disable event report - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F38
        ERACK: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F38(secsgem.secs.data_items.ERACK.CEID_UNKNOWN)
        S2F38
          <B 0x1> .

    Data Items:
        - :class:`ERACK <secsgem.secs.data_items.ERACK>`

    """

    _stream = 2
    _function = 38

    _data_format = ERACK

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
