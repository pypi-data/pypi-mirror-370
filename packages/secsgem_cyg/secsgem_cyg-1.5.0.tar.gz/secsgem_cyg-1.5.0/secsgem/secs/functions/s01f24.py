"""Class for stream 01 function 24."""

from secsgem.secs.data_items import CEID, CENAME, VID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F24(SecsStreamFunction):
    """Collection event namelist.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F24
        [
            {
                CEID: U1/U2/U4/U8/I1/I2/I4/I8/A
                CENAME: A
                VID: [
                    DATA: U1/U2/U4/U8/I1/I2/I4/I8/A
                    ...
                ]
            }
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F24([{"CEID": 1, "CENAME": "CE1", "VID": [1, "VARIABLEID"]}])
        S1F24
          <L [1]
            <L [3]
              <U1 1 >
              <A "CE1">
              <L [2]
                <U1 1 >
                <A "VARIABLEID">
              >
            >
          > .

    Data Items:
        - :class:`CEID <secsgem.secs.data_items.CEID>`
        - :class:`CENAME <secsgem.secs.data_items.CENAME>`
        - :class:`VID <secsgem.secs.data_items.VID>`

    """

    _stream = 1
    _function = 24

    _data_format = [
        [
            CEID,
            CENAME,
            [VID]
        ]
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
