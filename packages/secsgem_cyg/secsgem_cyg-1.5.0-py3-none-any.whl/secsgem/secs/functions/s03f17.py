"""Class for stream 03 function 17."""

from secsgem.secs.data_items import DATAID, CARRIERACTION, CARRIERID, CATTRDATA, CATTRID, PTN

from secsgem.secs.functions.base import SecsStreamFunction


class SecsS03F17(SecsStreamFunction):
    """Carrier Action Request."""

    _stream = 3
    _function = 17

    _data_format = [
        DATAID,
        CARRIERACTION,
        CARRIERID,
        PTN,
        [
            [
                "PARAMS",
                CATTRID,
                CATTRDATA
            ]
        ]
    ]

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = True
