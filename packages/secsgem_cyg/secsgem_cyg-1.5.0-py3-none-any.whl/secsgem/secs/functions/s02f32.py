from secsgem.secs.functions.base import SecsStreamFunction
from secsgem.secs.data_items.tiack import TIACK


class SecsS02F32(SecsStreamFunction):
    _stream = 2
    _function = 32

    _data_format = TIACK

    _to_host = True
    _to_equipment = False

    _has_reply = False
    _is_reply_required = False

    _is_multi_block = False
