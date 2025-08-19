"""Class for stream 02 function 18."""

from secsgem.secs.data_items import TIME
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS02F18(SecsStreamFunction):
    """date and time - data.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F18
        TIME: A[32]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS02F18("160816205942")
        S2F18
          <A "160816205942"> .

    Data Items:
        - :class:`TIME <secsgem.secs.data_items.TIME>`

    """

    _stream = 2
    _function = 18

    _data_format = TIME

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
