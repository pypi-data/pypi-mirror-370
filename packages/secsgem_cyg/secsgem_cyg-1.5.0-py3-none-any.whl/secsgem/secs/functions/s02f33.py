"""Class for stream 02 function 33."""

from secsgem.secs.data_items import DATAID, RPTID, VID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F33(SecsStreamFunction):
    """define report.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F33
        {
            DATAID: U1/U2/U4/U8/I1/I2/I4/I8/A
            DATA: [
                {
                    RPTID: U1/U2/U4/U8/I1/I2/I4/I8/A
                    VID: [
                        DATA: U1/U2/U4/U8/I1/I2/I4/I8/A
                        ...
                    ]
                }
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F33({"DATAID": 1, "DATA": [{"RPTID": 1000, "VID": [12, 1337]},
        ...     {"RPTID": 1001, "VID": [1, 2355]}]})
        S2F33 W
          <L [2]
            <U1 1 >
            <L [2]
              <L [2]
                <U2 1000 >
                <L [2]
                  <U1 12 >
                  <U2 1337 >
                >
              >
              <L [2]
                <U2 1001 >
                <L [2]
                  <U1 1 >
                  <U2 2355 >
                >
              >
            >
          > .

    Data Items:
        - :class:`DATAID <secsgem.secs.data_items.DATAID>`
        - :class:`RPTID <secsgem.secs.data_items.RPTID>`
        - :class:`VID <secsgem.secs.data_items.VID>`

    """

    _stream = 2
    _function = 33

    _data_format = [
        DATAID,
        [
            [
                RPTID,
                [VID]
            ]
        ]
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
