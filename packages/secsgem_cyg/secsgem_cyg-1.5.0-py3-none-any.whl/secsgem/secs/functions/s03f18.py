"""Class for stream 03 function 18."""

from secsgem.secs.data_items import CAACK, ERRCODE, ERRTEXT
from secsgem.secs.functions.base import SecsStreamFunction


class SecsS03F18(SecsStreamFunction):
    """Carrier Action Acknowledge."""

    _stream = 3
    _function = 18

    _data_format = [
        CAACK,
        [
            [
                "PARAMS",
                ERRCODE,
                ERRTEXT
            ]
        ]
    ]

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
