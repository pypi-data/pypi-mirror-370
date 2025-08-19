"""ECNAME data item."""
from .. import variables
from .base import DataItemBase


class ECNAME(DataItemBase):
    """Equipment constant name.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS02F30 <secsgem.secs.functions.SecsS02F30>`

    """

    __type__ = variables.String
