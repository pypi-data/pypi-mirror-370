"""RPSEL data item."""
from .. import variables
from .base import DataItemBase


class RPSEL(DataItemBase):
    """Reference point select.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`

    **Used In Function**
        - :class:`SecsS12F01 <secsgem.secs.functions.SecsS12F01>`
        - :class:`SecsS12F04 <secsgem.secs.functions.SecsS12F04>`

    """

    __type__ = variables.U1
