"""TID data item."""
from .. import variables
from .base import DataItemBase


class TID(DataItemBase):
    """Terminal ID.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Used In Function**
        - :class:`SecsS10F01 <secsgem.secs.functions.SecsS10F01>`
        - :class:`SecsS10F03 <secsgem.secs.functions.SecsS10F03>`

    """

    __type__ = variables.Binary
    __count__ = 1
