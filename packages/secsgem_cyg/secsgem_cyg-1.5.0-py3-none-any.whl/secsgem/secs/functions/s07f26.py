"""Class for stream 07 function 26."""

from secsgem.secs.data_items import PPID, MDLN, SOFTREV,CCODE, PPARM
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS07F26(SecsStreamFunction):
    """Format process program data..

    Args:
        value: parameters for this function (see example)
    """

    _stream = 7
    _function = 26

    _data_format = [
        PPID,
        MDLN,
        SOFTREV,
        [
            [
                "CCODE",
                CCODE,
                [PPARM]
            ]
        ]
    ]

    _to_host = True
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
