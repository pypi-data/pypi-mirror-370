"""Class for stream 12 function 09."""

from secsgem.secs.data_items import BINLT, IDTYP, MID, STRP
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F09(SecsStreamFunction):
    """map data type 2 - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F09
        {
            MID: A/B[80]
            IDTYP: B[1]
            STRP: I1/I2/I4/I8[2]
            BINLT: U1/A
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F09({
        ...     "MID": "materialID",
        ...     "IDTYP": secsgem.secs.data_items.IDTYP.WAFER,
        ...     "STRP": [0, 1],
        ...     "BINLT": [1, 2, 3, 4, 5, 6]})
        S12F9 W
          <L [4]
            <A "materialID">
            <B 0x0>
            <I1 0 1 >
            <U1 1 2 3 4 5 6 >
          > .

    Data Items:
        - :class:`MID <secsgem.secs.data_items.MID>`
        - :class:`IDTYP <secsgem.secs.data_items.IDTYP>`
        - :class:`STRP <secsgem.secs.data_items.STRP>`
        - :class:`BINLT <secsgem.secs.data_items.BINLT>`

    """

    _stream = 12
    _function = 9

    _data_format = [
        MID,
        IDTYP,
        STRP,
        BINLT
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
