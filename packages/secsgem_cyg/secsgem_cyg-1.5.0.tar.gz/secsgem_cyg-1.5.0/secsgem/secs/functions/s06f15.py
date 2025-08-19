"""Class for stream 06 function 15."""

from secsgem.secs.data_items import CEID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS06F15(SecsStreamFunction):
    """event report request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F15
        CEID: U1/U2/U4/U8/I1/I2/I4/I8/A

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F15(1337)
        S6F15 W
          <U2 1337 > .

    Data Items:
        - :class:`CEID <secsgem.secs.data_items.CEID>`

    """

    _stream = 6
    _function = 15

    _data_format = CEID

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
