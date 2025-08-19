"""Class for stream 02 function 25."""

from secsgem.secs.data_items import ABS
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F25(SecsStreamFunction):
    """Loopback diagnostic request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F25
        ABS: B

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F25("Text")
        S2F25 W
          <B 0x54 0x65 0x78 0x74> .

    Data Items:
        - :class:`ABS <secsgem.secs.data_items.ABS>`

    """

    _stream = 2
    _function = 25

    _data_format = ABS

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
