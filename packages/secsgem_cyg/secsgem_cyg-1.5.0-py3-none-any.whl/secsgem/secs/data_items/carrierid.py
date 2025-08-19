"""CARRIERID data item."""
from .. import variables
from .base import DataItemBase


class CARRIERID(DataItemBase):
    """Carrier id.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS03F17 <secsgem.secs.functions.SecsS03F17>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.U1,
        variables.U2,
        variables.U4,
        variables.U8,
        variables.I1,
        variables.I2,
        variables.I4,
        variables.I8,
        variables.String
    ]