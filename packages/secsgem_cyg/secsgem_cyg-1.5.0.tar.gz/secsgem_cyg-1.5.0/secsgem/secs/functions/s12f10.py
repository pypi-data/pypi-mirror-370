"""Class for stream 12 function 10."""

from secsgem.secs.data_items import MDACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F10(SecsStreamFunction):
    """map data type 2 - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F10
        MDACK: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F10(secsgem.secs.data_items.MDACK.ACK)
        S12F10
          <B 0x0> .

    Data Items:
        - :class:`MDACK <secsgem.secs.data_items.MDACK>`

    """

    _stream = 12
    _function = 10

    _data_format = MDACK

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
