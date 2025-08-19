"""Class for stream 12 function 07."""

from secsgem.secs.data_items import BINLT, IDTYP, MID, RSINF
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F07(SecsStreamFunction):
    """map data type 1 - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F07
        {
            MID: A/B[80]
            IDTYP: B[1]
            DATA: [
                {
                    RSINF: I1/I2/I4/I8[3]
                    BINLT: U1/A
                }
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F07({
        ...     "MID": "materialID",
        ...     "IDTYP": secsgem.secs.data_items.IDTYP.WAFER,
        ...     "DATA": [
        ...         {"RSINF": [1, 2, 3], "BINLT": [1, 2, 3, 4]},
        ...         {"RSINF": [4, 5, 6], "BINLT": [5, 6, 7, 8]}]})
        S12F7 W
          <L [3]
            <A "materialID">
            <B 0x0>
            <L [2]
              <L [2]
                <I1 1 2 3 >
                <U1 1 2 3 4 >
              >
              <L [2]
                <I1 4 5 6 >
                <U1 5 6 7 8 >
              >
            >
          > .

    Data Items:
        - :class:`MID <secsgem.secs.data_items.MID>`
        - :class:`IDTYP <secsgem.secs.data_items.IDTYP>`
        - :class:`RSINF <secsgem.secs.data_items.RSINF>`
        - :class:`BINLT <secsgem.secs.data_items.BINLT>`

    """

    _stream = 12
    _function = 7

    _data_format = [
        MID,
        IDTYP,
        [
            [
                RSINF,
                BINLT
            ]
        ]
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
