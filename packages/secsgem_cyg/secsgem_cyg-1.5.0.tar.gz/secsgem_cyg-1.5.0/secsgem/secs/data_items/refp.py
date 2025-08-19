"""REFP data item."""
from .. import variables
from .base import DataItemBase


class REFP(DataItemBase):
    """Reference point.

    :Types:
       - :class:`I1 <secsgem.secs.variables.I1>`
       - :class:`I2 <secsgem.secs.variables.I2>`
       - :class:`I4 <secsgem.secs.variables.I4>`
       - :class:`I8 <secsgem.secs.variables.I8>`

    **Used In Function**
        - :class:`SecsS12F01 <secsgem.secs.functions.SecsS12F01>`
        - :class:`SecsS12F04 <secsgem.secs.functions.SecsS12F04>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.I1,
        variables.I2,
        variables.I4,
        variables.I8
    ]
