"""EXRECVRA data item."""
from .. import variables
from .base import DataItemBase


class EXRECVRA(DataItemBase):
    """Exception recovery action.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 40

    **Used In Function**
        - :class:`SecsS05F09 <secsgem.secs.functions.SecsS05F09>`
        - :class:`SecsS05F13 <secsgem.secs.functions.SecsS05F13>`

    """

    __type__ = variables.String
    __count__ = 40
