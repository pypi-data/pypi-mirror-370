"""Class for stream 12 function 05."""

from secsgem.secs.data_items import IDTYP, MAPFT, MID, MLCL
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F05(SecsStreamFunction):
    """map transmit inquire.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F05
        {
            MID: A/B[80]
            IDTYP: B[1]
            MAPFT: B[1]
            MLCL: U1/U2/U4/U8
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F05({
        ...     "MID": "materialID",
        ...     "IDTYP": secsgem.secs.data_items.IDTYP.WAFER,
        ...     "MAPFT": secsgem.secs.data_items.MAPFT.ARRAY,
        ...     "MLCL": 0})
        S12F5 W
          <L [4]
            <A "materialID">
            <B 0x0>
            <B 0x1>
            <U1 0 >
          > .

    Data Items:
        - :class:`MID <secsgem.secs.data_items.MID>`
        - :class:`IDTYP <secsgem.secs.data_items.IDTYP>`
        - :class:`MAPFT <secsgem.secs.data_items.MAPFT>`
        - :class:`MLCL <secsgem.secs.data_items.MLCL>`

    """

    _stream = 12
    _function = 5

    _data_format = [
        MID,
        IDTYP,
        MAPFT,
        MLCL
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
