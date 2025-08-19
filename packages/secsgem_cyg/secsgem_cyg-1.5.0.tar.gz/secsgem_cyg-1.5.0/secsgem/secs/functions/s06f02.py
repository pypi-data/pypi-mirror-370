"""Class for stream 06 function 02."""

from secsgem.secs.data_items import ACKC6
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS06F02(SecsStreamFunction):
    """Trace data - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F02
        ACKC6: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F02(secsgem.secs.data_items.ACKC6.ACCEPTED)
        S6F2
          <B 0x0> .

    Data Items:
        - :class:`ACKC6 <secsgem.secs.data_items.ACKC6>`

    """

    _stream = 6
    _function = 2

    _data_format = ACKC6

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
