"""Class for stream 12 function 12."""

from secsgem.secs.data_items import MDACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F12(SecsStreamFunction):
    """map data type 3 - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F12
        MDACK: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F12(secsgem.secs.data_items.MDACK.FORMAT_ERROR)
        S12F12
          <B 0x1> .

    Data Items:
        - :class:`MDACK <secsgem.secs.data_items.MDACK>`

    """

    _stream = 12
    _function = 12

    _data_format = MDACK

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
