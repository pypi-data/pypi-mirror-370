"""Class for stream 01 function 23."""

from secsgem.secs.data_items import CEID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F23(SecsStreamFunction):
    """Collection event namelist request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F23
        [
            CEID: U1/U2/U4/U8/I1/I2/I4/I8/A
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F23([1, "COLLEVTID"])
        S1F23 W
          <L [2]
            <U1 1 >
            <A "COLLEVTID">
          > .

    Data Items:
        - :class:`CEID <secsgem.secs.data_items.CEID>`

    """

    _stream = 1
    _function = 23

    _data_format = [CEID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
