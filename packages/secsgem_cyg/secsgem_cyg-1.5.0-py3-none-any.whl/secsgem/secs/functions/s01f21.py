"""Class for stream 01 function 21."""

from secsgem.secs.data_items import VID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F21(SecsStreamFunction):
    """Data variable namelist request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F21
        [
            VID: U1/U2/U4/U8/I1/I2/I4/I8/A
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F21([1, "VARIABLEID"])
        S1F21 W
          <L [2]
            <U1 1 >
            <A "VARIABLEID">
          > .

    Data Items:
        - :class:`VID <secsgem.secs.data_items.VID>`

    """

    _stream = 1
    _function = 21

    _data_format = [VID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
