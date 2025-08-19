"""RCMD data item."""
from .. import variables
from .base import DataItemBase


class RCMD(DataItemBase):
    """Remote command.

    :Types:
       - :class:`U1 <secsgem.secs.variables.U1>`
       - :class:`I1 <secsgem.secs.variables.I1>`
       - :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS02F21 <secsgem.secs.functions.SecsS02F21>`
        - :class:`SecsS02F41 <secsgem.secs.functions.SecsS02F41>`
        - :class:`SecsS02F49 <secsgem.secs.functions.SecsS02F49>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.U1,
        variables.I1,
        variables.String
    ]
