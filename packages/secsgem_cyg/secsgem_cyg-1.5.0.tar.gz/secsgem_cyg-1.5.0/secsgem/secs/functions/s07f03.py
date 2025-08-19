"""Class for stream 07 function 03."""

from secsgem.secs.data_items import PPBODY, PPID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F03(SecsStreamFunction):
    """process program - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F03
        {
            PPID: A/B[120]
            PPBODY: U1/U2/U4/U8/I1/I2/I4/I8/A/B
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F03({"PPID": "program", "PPBODY": secsgem.secs.variables.Binary("data")})
        S7F3 W
          <L [2]
            <A "program">
            <B 0x64 0x61 0x74 0x61>
          > .

    Data Items:
        - :class:`PPID <secsgem.secs.data_items.PPID>`
        - :class:`PPBODY <secsgem.secs.data_items.PPBODY>`

    """

    _stream = 7
    _function = 3

    _data_format = [
        PPID,
        PPBODY
    ]

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
