"""Class for stream 05 function 05."""

from secsgem.secs.data_items import ALID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F05(SecsStreamFunction):
    """list alarms - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F05
        [
            ALID: U1/U2/U4/U8/I1/I2/I4/I8
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F05([100, 200])
        S5F5 W
          <L [2]
            <U1 100 >
            <U1 200 >
          > .

    Data Items:
        - :class:`ALID <secsgem.secs.data_items.ALID>`

    """

    _stream = 5
    _function = 5

    _data_format = [ALID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
