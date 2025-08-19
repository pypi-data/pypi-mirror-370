"""OBJSPEC data item."""
from .. import variables
from .base import DataItemBase


class OBJSPEC(DataItemBase):
    """Specific object instance.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS02F49 <secsgem.secs.functions.SecsS02F49>`
        - :class:`SecsS14F01 <secsgem.secs.functions.SecsS14F01>`
        - :class:`SecsS14F03 <secsgem.secs.functions.SecsS14F03>`

    """

    __type__ = variables.String
