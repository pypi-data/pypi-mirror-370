"""Class for stream 02 function 29."""

from secsgem.secs.data_items import ECID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F29(SecsStreamFunction):
    """equipment constant namelist - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F29
        [
            ECID: U1/U2/U4/U8/I1/I2/I4/I8/A
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F29([1, 1337])
        S2F29 W
          <L [2]
            <U1 1 >
            <U2 1337 >
          > .

    Data Items:
        - :class:`ECID <secsgem.secs.data_items.ECID>`

    An empty list will return all available equipment constants.

    """

    _stream = 2
    _function = 29

    _data_format = [ECID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
