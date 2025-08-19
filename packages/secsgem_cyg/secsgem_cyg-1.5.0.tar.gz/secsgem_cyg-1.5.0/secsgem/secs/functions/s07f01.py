"""Class for stream 07 function 01."""

from secsgem.secs.data_items import LENGTH, PPID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F01(SecsStreamFunction):
    """process program load - inquire.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F01
        {
            PPID: A/B[120]
            LENGTH: U1/U2/U4/U8/I1/I2/I4/I8
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F01({"PPID": "program", "LENGTH": 4})
        S7F1 W
          <L [2]
            <A "program">
            <U1 4 >
          > .

    Data Items:
        - :class:`PPID <secsgem.secs.data_items.PPID>`
        - :class:`LENGTH <secsgem.secs.data_items.LENGTH>`

    """

    _stream = 7
    _function = 1

    _data_format = [
        PPID,
        LENGTH
    ]

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
