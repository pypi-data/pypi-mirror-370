"""EXTYPE data item."""
from .. import variables
from .base import DataItemBase


class EXTYPE(DataItemBase):
    """Exception type.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS05F09 <secsgem.secs.functions.SecsS05F09>`
        - :class:`SecsS05F11 <secsgem.secs.functions.SecsS05F11>`

    """

    __type__ = variables.String
