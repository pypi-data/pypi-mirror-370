"""CPVAL data item."""
from .. import variables
from .base import DataItemBase


class CPVAL(DataItemBase):
    """Command parameter value.

    :Types:
       - :class:`Boolean <secsgem.secs.variables.Boolean>`
       - :class:`U1 <secsgem.secs.variables.U1>`
       - :class:`U2 <secsgem.secs.variables.U2>`
       - :class:`U4 <secsgem.secs.variables.U4>`
       - :class:`U8 <secsgem.secs.variables.U8>`
       - :class:`I1 <secsgem.secs.variables.I1>`
       - :class:`I2 <secsgem.secs.variables.I2>`
       - :class:`I4 <secsgem.secs.variables.I4>`
       - :class:`I8 <secsgem.secs.variables.I8>`
       - :class:`String <secsgem.secs.variables.String>`
       - :class:`Binary <secsgem.secs.variables.Binary>`

    **Used In Function**
        - :class:`SecsS02F41 <secsgem.secs.functions.SecsS02F41>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.Boolean,
        variables.U1,
        variables.U2,
        variables.U4,
        variables.U8,
        variables.I1,
        variables.I2,
        variables.I4,
        variables.I8,
        variables.String,
        variables.Binary,
        variables.Array
    ]
