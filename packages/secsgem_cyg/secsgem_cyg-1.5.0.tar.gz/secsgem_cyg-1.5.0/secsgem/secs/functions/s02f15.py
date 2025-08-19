"""Class for stream 02 function 15."""

from secsgem.secs.data_items import ECID, ECV
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F15(SecsStreamFunction):
    """new equipment constant - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F15
        [
            {
                ECID: U1/U2/U4/U8/I1/I2/I4/I8/A
                ECV: L/BOOLEAN/I8/I1/I2/I4/F8/F4/U8/U1/U2/U4/A/B
            }
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F15([
        ...     {"ECID": 1, "ECV": secsgem.secs.variables.U4(10)},
        ...     {"ECID": "1337", "ECV": "text"}])
        S2F15 W
          <L [2]
            <L [2]
              <U1 1 >
              <U4 10 >
            >
            <L [2]
              <A "1337">
              <A "text">
            >
          > .

    Data Items:
        - :class:`ECID <secsgem.secs.data_items.ECID>`
        - :class:`ECV <secsgem.secs.data_items.ECV>`

    """

    _stream = 2
    _function = 15

    _data_format = [
        [
            ECID,
            ECV
        ]
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
