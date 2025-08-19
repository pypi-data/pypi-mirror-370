"""Class for stream 06 function 24."""

from secsgem.secs.data_items import RSDA
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS06F24(SecsStreamFunction):
    """Request spooled data acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F24
        RSDA: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F24(secsgem.secs.data_items.RSDA.ACK)
        S6F24
          <B 0x0> .

    Data Items:
        - :class:`RSDA <secsgem.secs.data_items.RSDA>`

    """

    _stream = 6
    _function = 24

    _data_format = RSDA

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
