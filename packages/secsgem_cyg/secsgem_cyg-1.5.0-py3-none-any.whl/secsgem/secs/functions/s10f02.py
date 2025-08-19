"""Class for stream 10 function 02."""

from secsgem.secs.data_items import ACKC10
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS10F02(SecsStreamFunction):
    """terminal - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F02
        ACKC10: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F02(secsgem.secs.data_items.ACKC10.ACCEPTED)
        S10F2
          <B 0x0> .

    Data Items:
        - :class:`ACKC10 <secsgem.secs.data_items.ACKC10>`

    """

    _stream = 10
    _function = 2

    _data_format = ACKC10

    _to_host = False
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
