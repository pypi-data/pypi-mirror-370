"""Class for stream 01 function 02."""

from secsgem.secs.data_items import MDLN
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F02(SecsStreamFunction):
    """on line data.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F02
        [
            MDLN: A[20]
            ...
        ]

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F02(["secsgem", "0.0.6"]) # E->H
        S1F2
          <L [2]
            <A "secsgem">
            <A "0.0.6">
          > .
        >>> secsgem.secs.functions.SecsS01F02() # H->E
        S1F2
          <L> .

    Data Items:
        - :class:`MDLN <secsgem.secs.data_items.MDLN>`

    .. caution::

        This Stream/function has different structures depending on the source.
        If it is sent from the eqipment side it has the structure below, if it
        is sent from the host it is an empty list.
        Be sure to fill the array accordingly.

    **Structure E->H**::

        {
            MDLN: A[20]
            SOFTREV: A[20]
        }

    """

    _stream = 1
    _function = 2

    _data_format = [MDLN]

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
