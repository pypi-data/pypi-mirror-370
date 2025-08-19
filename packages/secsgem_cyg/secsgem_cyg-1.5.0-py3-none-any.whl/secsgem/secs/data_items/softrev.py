"""SOFTREV data item."""
from .. import variables
from .base import DataItemBase


class SOFTREV(DataItemBase):
    """Software revision.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 20

    """

    __type__ = variables.String
    __count__ = 20
