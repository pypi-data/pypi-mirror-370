"""Class for stream 06 function 07."""

from secsgem.secs.data_items import DATAID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS06F07(SecsStreamFunction):
    """data transfer request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F07
        DATAID: U1/U2/U4/U8/I1/I2/I4/I8/A

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F07(1)
        S6F7 W
          <U1 1 > .

    Data Items:
        - :class:`DATAID <secsgem.secs.data_items.DATAID>`

    """

    _stream = 6
    _function = 7

    _data_format = DATAID

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
