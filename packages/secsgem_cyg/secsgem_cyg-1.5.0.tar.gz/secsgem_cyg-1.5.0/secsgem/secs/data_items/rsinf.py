"""RSINF data item."""
from .. import variables
from .base import DataItemBase


class RSINF(DataItemBase):
    """Starting location.

    :Types:
       - :class:`I1 <secsgem.secs.variables.I1>`
       - :class:`I2 <secsgem.secs.variables.I2>`
       - :class:`I4 <secsgem.secs.variables.I4>`
       - :class:`I8 <secsgem.secs.variables.I8>`
    :Length: 3

    **Used In Function**
        - :class:`SecsS12F07 <secsgem.secs.functions.SecsS12F07>`
        - :class:`SecsS12F14 <secsgem.secs.functions.SecsS12F14>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.I1,
        variables.I2,
        variables.I4,
        variables.I8
    ]
    __count__ = 3
