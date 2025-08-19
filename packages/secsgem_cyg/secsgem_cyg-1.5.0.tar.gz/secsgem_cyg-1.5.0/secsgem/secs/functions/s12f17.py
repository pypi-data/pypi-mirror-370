"""Class for stream 12 function 17."""

from secsgem.secs.data_items import IDTYP, MID, SDBIN
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F17(SecsStreamFunction):
    """map data type 3 - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F17
        {
            MID: A/B[80]
            IDTYP: B[1]
            SDBIN: B[1]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F17({
        ...     "MID": "materialID",
        ...     "IDTYP": secsgem.secs.data_items.IDTYP.WAFER,
        ...     "SDBIN": secsgem.secs.data_items.SDBIN.DONT_SEND})
        S12F17 W
          <L [3]
            <A "materialID">
            <B 0x0>
            <B 0x1>
          > .

    Data Items:
        - :class:`MID <secsgem.secs.data_items.MID>`
        - :class:`IDTYP <secsgem.secs.data_items.IDTYP>`
        - :class:`SDBIN <secsgem.secs.data_items.SDBIN>`

    """

    _stream = 12
    _function = 17

    _data_format = [
        MID,
        IDTYP,
        SDBIN
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
