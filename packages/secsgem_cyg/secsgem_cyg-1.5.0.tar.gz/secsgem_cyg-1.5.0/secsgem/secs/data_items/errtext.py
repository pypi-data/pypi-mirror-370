"""ERRTEXT data item."""
from .. import variables
from .base import DataItemBase


class ERRTEXT(DataItemBase):
    """Error description for error code.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 120

    **Used In Function**
        - :class:`SecsS03F18 <secsgem.secs.functions.SecsS03F18>`
        - :class:`SecsS05F14 <secsgem.secs.functions.SecsS05F14>`
        - :class:`SecsS05F15 <secsgem.secs.functions.SecsS05F15>`
        - :class:`SecsS05F18 <secsgem.secs.functions.SecsS05F18>`
        - :class:`SecsS14F02 <secsgem.secs.functions.SecsS14F02>`
        - :class:`SecsS14F04 <secsgem.secs.functions.SecsS14F04>`

    """

    __type__ = variables.String
    __count__ = 120
