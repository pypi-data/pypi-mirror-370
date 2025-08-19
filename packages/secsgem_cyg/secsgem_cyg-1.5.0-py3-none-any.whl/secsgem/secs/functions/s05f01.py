"""Class for stream 05 function 01."""

from secsgem.secs.data_items import ALCD, ALID, ALTX
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F01(SecsStreamFunction):
    """alarm report - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F01
        {
            ALCD: B[1]
            ALID: U1/U2/U4/U8/I1/I2/I4/I8
            ALTX: A[120]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F01({
        ...     "ALCD": secsgem.secs.data_items.ALCD.PERSONAL_SAFETY |
        ...             secsgem.secs.data_items.ALCD.ALARM_SET,
        ...     "ALID": 100,
        ...     "ALTX": "text"})
        S5F1
          <L [3]
            <B 0x81>
            <U1 100 >
            <A "text">
          > .

    Data Items:
        - :class:`ALCD <secsgem.secs.data_items.ALCD>`
        - :class:`ALID <secsgem.secs.data_items.ALID>`
        - :class:`ALTX <secsgem.secs.data_items.ALTX>`

    """

    _stream = 5
    _function = 1

    _data_format = [
        ALCD,
        ALID,
        ALTX
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = False

    _is_multi_block = False
