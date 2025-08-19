"""XDIES data item."""
from .. import variables
from .base import DataItemBase


class XDIES(DataItemBase):
    """Die size/index X-axis.

    :Types:
       - :class:`U1 <secsgem.secs.variables.U1>`
       - :class:`U2 <secsgem.secs.variables.U2>`
       - :class:`U4 <secsgem.secs.variables.U4>`
       - :class:`U8 <secsgem.secs.variables.U8>`
       - :class:`F4 <secsgem.secs.variables.F4>`
       - :class:`F8 <secsgem.secs.variables.F8>`

    **Used In Function**
        - :class:`SecsS12F01 <secsgem.secs.functions.SecsS12F01>`
        - :class:`SecsS12F04 <secsgem.secs.functions.SecsS12F04>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.U1,
        variables.U2,
        variables.U4,
        variables.U8,
        variables.F4,
        variables.F8
    ]
