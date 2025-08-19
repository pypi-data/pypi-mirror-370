"""Class for stream 10 function 03."""

from secsgem.secs.data_items import TEXT, TID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS10F03(SecsStreamFunction):
    """terminal single - display.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F03
        {
            TID: B[1]
            TEXT: U1/U2/U4/U8/I1/I2/I4/I8/A/B
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS10F03({"TID": 0, "TEXT": "hello!"})
        S10F3
          <L [2]
            <B 0x0>
            <A "hello!">
          > .

    Data Items:
        - :class:`TID <secsgem.secs.data_items.TID>`
        - :class:`TEXT <secsgem.secs.data_items.TEXT>`

    """

    _stream = 10
    _function = 3

    _data_format = [
        TID,
        TEXT
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = False

    _is_multi_block = False
