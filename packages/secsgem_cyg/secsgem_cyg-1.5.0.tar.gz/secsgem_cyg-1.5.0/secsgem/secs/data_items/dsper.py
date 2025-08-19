"""DSPER data item."""
from .. import variables
from .base import DataItemBase


class DSPER(DataItemBase):
    """Data sample period.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS02F23 <secsgem.secs.functions.SecsS02F23>`

    """

    __type__ = variables.String
