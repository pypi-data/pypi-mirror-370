"""Class for stream 02 function 37."""

from secsgem.secs.data_items import CEED, CEID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F37(SecsStreamFunction):
    """en-/disable event report.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F37
        {
            CEED: BOOLEAN[1]
            CEID: [
                DATA: U1/U2/U4/U8/I1/I2/I4/I8/A
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F37({"CEED": True, "CEID": [1337]})
        S2F37 W
          <L [2]
            <BOOLEAN True >
            <L [1]
              <U2 1337 >
            >
          > .

    Data Items:
        - :class:`CEED <secsgem.secs.data_items.CEED>`
        - :class:`CEID <secsgem.secs.data_items.CEID>`

    """

    _stream = 2
    _function = 37

    _data_format = [
        CEED,
        [CEID]
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
