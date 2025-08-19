"""Class for stream 02 function 47."""

from secsgem.secs.data_items import VID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F47(SecsStreamFunction):
    """Variable limit attribute request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F47
        [
            VID: U1/U2/U4/U8/I1/I2/I4/I8/A
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F47([1, "VARIABLEID"])
        S2F47 W
          <L [2]
            <U1 1 >
            <A "VARIABLEID">
          > .

    Data Items:
        - :class:`VID <secsgem.secs.data_items.VID>`

    """

    _stream = 2
    _function = 47

    _data_format = [VID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
