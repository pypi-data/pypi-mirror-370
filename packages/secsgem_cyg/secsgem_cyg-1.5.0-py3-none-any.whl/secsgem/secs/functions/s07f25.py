"""Class for stream 07 function 25."""

from secsgem.secs.data_items import PPID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F25(SecsStreamFunction):
    """process program - request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F25
        PPID: A/B[120]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F25("program")
        S7F25 W
          <A "program"> .

    Data Items:
        - :class:`PPID <secsgem.secs.data_items.PPID>`

    """

    _stream = 7
    _function = 25

    _data_format = PPID

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
