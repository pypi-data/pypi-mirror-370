"""Class for stream 07 function 06."""

from secsgem.secs.data_items import PPBODY, PPID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F06(SecsStreamFunction):
    """process program - data.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F06
        {
            PPID: A/B[120]
            PPBODY: U1/U2/U4/U8/I1/I2/I4/I8/A/B
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F06({"PPID": "program", "PPBODY": secsgem.secs.variables.Binary("data")})
        S7F6
          <L [2]
            <A "program">
            <B 0x64 0x61 0x74 0x61>
          > .

    Data Items:
        - :class:`PPID <secsgem.secs.data_items.PPID>`
        - :class:`PPBODY <secsgem.secs.data_items.PPBODY>`

    """

    _stream = 7
    _function = 6

    _data_format = [
        PPID,
        PPBODY
    ]

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = True
