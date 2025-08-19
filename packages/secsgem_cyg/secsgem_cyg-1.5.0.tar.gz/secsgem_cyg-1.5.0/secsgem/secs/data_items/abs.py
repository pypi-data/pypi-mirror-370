"""ABS data item."""
from .. import variables
from .base import DataItemBase


class ABS(DataItemBase):
    """Any binary string.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`

    **Used In Function**
        - :class:`SecsS02F25 <secsgem.secs.functions.SecsS02F25>`
        - :class:`SecsS02F26 <secsgem.secs.functions.SecsS02F26>`

    """

    __type__ = variables.Binary
