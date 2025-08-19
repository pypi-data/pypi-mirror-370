from secsgem.secs.functions.base import SecsStreamFunction
from secsgem.secs.data_items import TIME


class SecsS02F31(SecsStreamFunction):
    _stream = 2
    _function = 31

    _data_format = TIME

    _to_host = False
    _to_equipment = True

    _has_reply = True
    _is_reply_required = True

    _is_multi_block = False
