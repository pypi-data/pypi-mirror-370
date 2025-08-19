"""CEED data item."""
from .. import variables
from .base import DataItemBase


class CEED(DataItemBase):
    """Collection event or trace enable/disable code.

    :Type: :class:`Boolean <secsgem.secs.variables.Boolean>`
    :Length: 1

    **Values**
        +-------+---------+
        | Value |         |
        +=======+=========+
        | True  | Enable  |
        +-------+---------+
        | False | Disable |
        +-------+---------+

    **Used In Function**
        - :class:`SecsS02F37 <secsgem.secs.functions.SecsS02F37>`

    """

    __type__ = variables.Boolean
    __count__ = 1
