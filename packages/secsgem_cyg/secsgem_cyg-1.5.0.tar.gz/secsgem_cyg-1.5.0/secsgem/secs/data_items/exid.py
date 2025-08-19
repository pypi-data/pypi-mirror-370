"""EXID data item."""
from .. import variables
from .base import DataItemBase


class EXID(DataItemBase):
    """Exception identifier.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 20

    **Used In Function**
        - :class:`SecsS05F09 <secsgem.secs.functions.SecsS05F09>`
        - :class:`SecsS05F11 <secsgem.secs.functions.SecsS05F11>`
        - :class:`SecsS05F13 <secsgem.secs.functions.SecsS05F13>`
        - :class:`SecsS05F14 <secsgem.secs.functions.SecsS05F14>`
        - :class:`SecsS05F15 <secsgem.secs.functions.SecsS05F15>`
        - :class:`SecsS05F17 <secsgem.secs.functions.SecsS05F17>`
        - :class:`SecsS05F18 <secsgem.secs.functions.SecsS05F18>`

    """

    __type__ = variables.String
    __count__ = 20
