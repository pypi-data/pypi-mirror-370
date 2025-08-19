"""MHEAD data item."""
from .. import variables
from .base import DataItemBase


class MHEAD(DataItemBase):
    """SECS message header.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 10

    **Used In Function**
        - :class:`SecsS09F01 <secsgem.secs.functions.SecsS09F01>`
        - :class:`SecsS09F03 <secsgem.secs.functions.SecsS09F03>`
        - :class:`SecsS09F05 <secsgem.secs.functions.SecsS09F05>`
        - :class:`SecsS09F07 <secsgem.secs.functions.SecsS09F07>`
        - :class:`SecsS09F11 <secsgem.secs.functions.SecsS09F11>`

    """

    __type__ = variables.Binary
    __count__ = 10
