"""Class for stream 02 function 35."""

from secsgem.secs.data_items import CEID, DATAID, RPTID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F35(SecsStreamFunction):
    """link event report.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F35
        {
            DATAID: U1/U2/U4/U8/I1/I2/I4/I8/A
            DATA: [
                {
                    CEID: U1/U2/U4/U8/I1/I2/I4/I8/A
                    RPTID: [
                        DATA: U1/U2/U4/U8/I1/I2/I4/I8/A
                        ...
                    ]
                }
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F35({"DATAID": 1, "DATA": [{"CEID": 1337, "RPTID": [1000, 1001]}]})
        S2F35 W
          <L [2]
            <U1 1 >
            <L [1]
              <L [2]
                <U2 1337 >
                <L [2]
                  <U2 1000 >
                  <U2 1001 >
                >
              >
            >
          > .

    Data Items:
        - :class:`DATAID <secsgem.secs.data_items.DATAID>`
        - :class:`CEID <secsgem.secs.data_items.CEID>`
        - :class:`RPTID <secsgem.secs.data_items.RPTID>`

    """

    _stream = 2
    _function = 35

    _data_format = [
        DATAID,
        [
            [
                CEID,
                [RPTID]
            ]
        ]
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
