"""ACKA data item."""
from .. import variables
from .base import DataItemBase


class ACKA(DataItemBase):
    """Request success.

    :Type: :class:`Boolean <secsgem.secs.variables.Boolean>`
    :Length: 1

    **Values**
        +-------+---------+
        | Value |         |
        +=======+=========+
        | True  | Success |
        +-------+---------+
        | False | Failed  |
        +-------+---------+

    **Used In Function**
        - :class:`SecsS05F14 <secsgem.secs.functions.SecsS05F14>`
        - :class:`SecsS05F15 <secsgem.secs.functions.SecsS05F15>`
        - :class:`SecsS05F18 <secsgem.secs.functions.SecsS05F18>`

    """

    __type__ = variables.Boolean
    __count__ = 1
