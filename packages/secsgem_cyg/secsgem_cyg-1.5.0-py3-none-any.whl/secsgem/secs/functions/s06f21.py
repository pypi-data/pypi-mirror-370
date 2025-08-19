"""Class for stream 06 function 21."""

from secsgem.secs.data_items import RPTID
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS06F21(SecsStreamFunction):
    """annotated individual report request.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F21
        RPTID: U1/U2/U4/U8/I1/I2/I4/I8/A

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS06F21(secsgem.secs.variables.U4(1337))
        S6F21 W
          <U4 1337 > .

    Data Items:
        - :class:`RPTID <secsgem.secs.data_items.RPTID>`

    """

    _stream = 6
    _function = 21

    _data_format = RPTID

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
