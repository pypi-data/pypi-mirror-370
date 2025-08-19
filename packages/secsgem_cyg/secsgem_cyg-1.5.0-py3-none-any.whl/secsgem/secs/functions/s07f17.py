"""Class for stream 07 function 17."""

from secsgem.secs.data_items import PPID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F17(SecsStreamFunction):
    """delete process program - send.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F17
        [
            PPID: A/B[120]
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F17(["program1", "program2"])
        S7F17 W
          <L [2]
            <A "program1">
            <A "program2">
          > .

    Data Items:
        - :class:`PPID <secsgem.secs.data_items.PPID>`

    """

    _stream = 7
    _function = 17

    _data_format = [PPID]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
