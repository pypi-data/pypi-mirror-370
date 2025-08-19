"""Class for stream 09 function 13."""

from secsgem.secs.data_items import EDID, MEXP
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS09F13(SecsStreamFunction):
    """conversation timeout.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F13
        {
            MEXP: A[6]
            EDID: U1/U2/U4/U8/I1/I2/I4/I8/A/B
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS09F13({"MEXP": "S01E01", "EDID": "data"})
        S9F13
          <L [2]
            <A "S01E01">
            <A "data">
          > .

    Data Items:
        - :class:`MEXP <secsgem.secs.data_items.MEXP>`
        - :class:`EDID <secsgem.secs.data_items.EDID>`

    """

    _stream = 9
    _function = 13

    _data_format = [
        MEXP,
        EDID
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
