"""DATLC data item."""
from .. import variables
from .base import DataItemBase


class DATLC(DataItemBase):
    """Data location.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`

    **Used In Function**
        - :class:`SecsS12F19 <secsgem.secs.functions.SecsS12F19>`

    """

    __type__ = variables.U1
