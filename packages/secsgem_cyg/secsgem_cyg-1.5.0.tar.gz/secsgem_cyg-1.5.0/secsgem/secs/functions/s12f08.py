"""Class for stream 12 function 08."""

from secsgem.secs.data_items import MDACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F08(SecsStreamFunction):
    """map data type 1 - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F08
        MDACK: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F08(secsgem.secs.data_items.MDACK.ABORT_MAP)
        S12F8
          <B 0x3> .

    Data Items:
        - :class:`MDACK <secsgem.secs.data_items.MDACK>`

    """

    _stream = 12
    _function = 8

    _data_format = MDACK

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
