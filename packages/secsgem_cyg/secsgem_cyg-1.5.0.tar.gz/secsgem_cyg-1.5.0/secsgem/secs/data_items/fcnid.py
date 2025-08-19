"""FCNID data item."""
from .. import variables
from .base import DataItemBase


class FCNID(DataItemBase):
    """Function ID.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`
    :Length: 1

    **Used In Function**
        - :class:`SecsS02F43 <secsgem.secs.functions.SecsS02F43>`
        - :class:`SecsS02F44 <secsgem.secs.functions.SecsS02F44>`

    """

    __type__ = variables.U1
    __count__ = 1
