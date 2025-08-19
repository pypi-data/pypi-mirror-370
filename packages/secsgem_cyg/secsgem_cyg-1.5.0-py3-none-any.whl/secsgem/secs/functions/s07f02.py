"""Class for stream 07 function 02."""

from secsgem.secs.data_items import PPGNT
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F02(SecsStreamFunction):
    """process program load - grant.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F02
        PPGNT: B[1]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS07F02(secsgem.secs.data_items.PPGNT.OK)
        S7F2
          <B 0x0> .

    Data Items:
        - :class:`PPGNT <secsgem.secs.data_items.PPGNT>`

    """

    _stream = 7
    _function = 2

    _data_format = PPGNT

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
