"""SMPLN data item."""
from .. import variables
from .base import DataItemBase


class SMPLN(DataItemBase):
    """Sample number.

    :Types:
       - :class:`I1 <secsgem.secs.variables.I1>`
       - :class:`I2 <secsgem.secs.variables.I2>`
       - :class:`I4 <secsgem.secs.variables.I4>`
       - :class:`I8 <secsgem.secs.variables.I8>`
       - :class:`U1 <secsgem.secs.variables.U1>`
       - :class:`U2 <secsgem.secs.variables.U2>`
       - :class:`U4 <secsgem.secs.variables.U4>`
       - :class:`U8 <secsgem.secs.variables.U8>`

    **Used In Function**
        - :class:`SecsS06F01 <secsgem.secs.functions.SecsS06F01>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.I1,
        variables.I2,
        variables.I4,
        variables.I8,
        variables.U1,
        variables.U2,
        variables.U4,
        variables.U8
    ]
