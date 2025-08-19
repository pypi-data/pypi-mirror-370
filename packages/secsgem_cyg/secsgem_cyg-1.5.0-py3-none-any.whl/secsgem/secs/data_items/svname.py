"""SVNAME data item."""
from .. import variables
from .base import DataItemBase


class SVNAME(DataItemBase):
    """Status variable name.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS01F12 <secsgem.secs.functions.SecsS01F12>`

    """

    __type__ = variables.String
