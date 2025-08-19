"""Class for stream 12 function 13."""

from secsgem.secs.data_items import IDTYP, MID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS12F13(SecsStreamFunction):
    """map data type 1 - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F13
        {
            MID: A/B[80]
            IDTYP: B[1]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS12F13({"MID": "materialID", "IDTYP": secsgem.secs.data_items.IDTYP.WAFER})
        S12F13 W
          <L [2]
            <A "materialID">
            <B 0x0>
          > .

    Data Items:
        - :class:`MID <secsgem.secs.data_items.MID>`
        - :class:`IDTYP <secsgem.secs.data_items.IDTYP>`

    """

    _stream = 12
    _function = 13

    _data_format = [
        MID,
        IDTYP
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
