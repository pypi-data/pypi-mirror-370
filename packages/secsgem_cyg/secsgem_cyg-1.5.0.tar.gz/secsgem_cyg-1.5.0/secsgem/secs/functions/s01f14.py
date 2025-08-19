"""Class for stream 01 function 14."""

from secsgem.secs.data_items import COMMACK, MDLN
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS01F14(SecsStreamFunction):
    """establish communication - acknowledge.

    Args:
        value: parameters for this function (see example)

    Examples:
        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F14
        {
            COMMACK: B[1]
            MDLN: [
                DATA: A[20]
                ...
            ]
        }

        >>> import secsgem.secs
        >>> secsgem.secs.functions.SecsS01F14({"COMMACK": secsgem.secs.data_items.COMMACK.ACCEPTED,
        ...     "MDLN": ["secsgem", "0.0.6"]})
        S1F14
          <L [2]
            <B 0x0>
            <L [2]
              <A "secsgem">
              <A "0.0.6">
            >
          > .

    Data Items:
        - :class:`COMMACK <secsgem.secs.data_items.COMMACK>`
        - :class:`MDLN <secsgem.secs.data_items.MDLN>`

    .. caution::

        This Stream/function has different structures depending on the source.
        See structure definition below for details.
        Be sure to fill the array accordingly.

    **Structure E->H**::

        {
            COMMACK: B[1]
            DATA: {
                MDLN: A[20]
                SOFTREV: A[20]
            }
        }

    **Structure H->E**::

        {
            COMMACK: B[1]
            DATA: []
        }

    """

    _stream = 1
    _function = 14

    _data_format = [
        COMMACK,
        [MDLN]
    ]

    _to_host = True
    _to_equipment = True

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
