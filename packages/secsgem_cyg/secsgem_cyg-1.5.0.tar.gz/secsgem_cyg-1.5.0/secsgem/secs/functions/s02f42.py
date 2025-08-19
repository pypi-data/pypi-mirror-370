"""Class for stream 02 function 42."""

from secsgem.secs.data_items import CPACK, CPNAME, HCACK
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F42(SecsStreamFunction):
    """host command - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F42
        {
            HCACK: B[1]
            PARAMS: [
                {
                    CPNAME: U1/U2/U4/U8/I1/I2/I4/I8/A
                    CPACK: B[1]
                }
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F42({
        ...     "HCACK": secsgem.secs.data_items.HCACK.INVALID_COMMAND,
        ...     "PARAMS": [
        ...         {"CPNAME": "PARAM1", "CPACK": secsgem.secs.data_items.CPACK.CPVAL_ILLEGAL_VALUE},
        ...         {"CPNAME": "PARAM2", "CPACK": secsgem.secs.data_items.CPACK.CPVAL_ILLEGAL_FORMAT}]})
        S2F42
          <L [2]
            <B 0x1>
            <L [2]
              <L [2]
                <A "PARAM1">
                <B 0x2>
              >
              <L [2]
                <A "PARAM2">
                <B 0x3>
              >
            >
          > .

    Data Items:
        - :class:`HCACK <secsgem.secs.data_items.HCACK>`
        - :class:`CPNAME <secsgem.secs.data_items.CPNAME>`
        - :class:`CPACK <secsgem.secs.data_items.CPACK>`

    """

    _stream = 2
    _function = 42

    _data_format = [
        HCACK,
        [
            [
                "PARAMS",
                CPNAME,
                CPACK
            ]
        ]
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
