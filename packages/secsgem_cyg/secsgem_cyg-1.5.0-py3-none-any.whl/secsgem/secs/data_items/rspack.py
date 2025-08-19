"""RSPACK data item."""
from .. import variables
from .base import DataItemBase


class RSPACK(DataItemBase):
    """Reset spooling acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+--------------------------------------+--------------------------------------------------+
        | Value | Description                          | Constant                                         |
        +=======+======================================+==================================================+
        | 0     | Acknowledge, spooling setup accepted | :const:`secsgem.secs.data_items.RSPACK.ACK`      |
        +-------+--------------------------------------+--------------------------------------------------+
        | 1     | Spooling setup rejected              | :const:`secsgem.secs.data_items.RSPACK.REJECTED` |
        +-------+--------------------------------------+--------------------------------------------------+
        | 2-63  | Reserved                             |                                                  |
        +-------+--------------------------------------+--------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F44 <secsgem.secs.functions.SecsS02F44>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    REJECTED = 1
