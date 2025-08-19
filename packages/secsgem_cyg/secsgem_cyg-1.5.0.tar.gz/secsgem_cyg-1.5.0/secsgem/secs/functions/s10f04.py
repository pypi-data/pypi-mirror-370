"""Class for stream 10 function 04."""

from secsgem.secs.data_items import ACKC10
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS10F04(SecsStreamFunction):
    """terminal single - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F04
        ACKC10: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F04(secsgem.secs.data_items.ACKC10.TERMINAL_NOT_AVAILABLE)
        S10F4
          <B 0x2> .

    Data Items:
        - :class:`ACKC10 <secsgem.secs.data_items.ACKC10>`

    """

    _stream = 10
    _function = 4

    _data_format = ACKC10

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
