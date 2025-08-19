"""Class for stream 02 function 26."""

from secsgem.secs.data_items import ABS
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F26(SecsStreamFunction):
    """Loopback diagnostic data.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F26
        ABS: B

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F26("Text")
        S2F26
          <B 0x54 0x65 0x78 0x74> .

    Data Items:
        - :class:`ABS <secsgem.secs.data_items.ABS>`

    """

    _stream = 2
    _function = 26

    _data_format = ABS

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
