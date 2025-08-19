"""RSDC data item."""
from .. import variables
from .base import DataItemBase


class RSDC(DataItemBase):
    """Request spooled data command.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`
    :Length: 1

    **Values**
        +-------+---------------------------+------------------------------------------------+
        | Value | Description               | Constant                                       |
        +=======+===========================+================================================+
        | 0     | Transmit spooled messages | :const:`secsgem.secs.data_items.RSDC.TRANSMIT` |
        +-------+---------------------------+------------------------------------------------+
        | 1     | Purge spooled messages    | :const:`secsgem.secs.data_items.RSDC.PURGE`    |
        +-------+---------------------------+------------------------------------------------+
        | 2-63  | Reserved                  |                                                |
        +-------+---------------------------+------------------------------------------------+

    **Used In Function**
        - :class:`SecsS06F23 <secsgem.secs.functions.SecsS06F23>`

    """

    __type__ = variables.U1
    __count__ = 1

    TRANSMIT = 0
    PURGE = 1
