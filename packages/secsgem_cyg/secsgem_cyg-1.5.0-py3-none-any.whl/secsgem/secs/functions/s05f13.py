"""Class for stream 05 function 13."""

from secsgem.secs.data_items import EXID, EXRECVRA
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS05F13(SecsStreamFunction):
    """exception recover - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F13
        {
            EXID: A[20]
            EXRECVRA: A[40]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS05F13({"EXID": "EX123", "EXRECVRA": "EXRECVRA2"})
        S5F13 W
          <L [2]
            <A "EX123">
            <A "EXRECVRA2">
          > .

    Data Items:
        - :class:`EXID <secsgem.secs.data_items.EXID>`
        - :class:`EXRECVRA <secsgem.secs.data_items.EXRECVRA>`

    """

    _stream = 5
    _function = 13

    _data_format = [
        EXID,
        EXRECVRA
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
