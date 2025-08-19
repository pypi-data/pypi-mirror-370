"""ACKC10 data item."""
from .. import variables
from .base import DataItemBase


class ACKC10(DataItemBase):
    """Acknowledge code for stream 10.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+------------------------+----------------------------------------------------------------+
        | Value | Description            | Constant                                                       |
        +=======+========================+================================================================+
        | 0     | Accepted               | :const:`secsgem.secs.data_items.ACKC10.ACCEPTED`               |
        +-------+------------------------+----------------------------------------------------------------+
        | 1     | Will not be displayed  | :const:`secsgem.secs.data_items.ACKC10.NOT_DISPLAYED`          |
        +-------+------------------------+----------------------------------------------------------------+
        | 2     | Terminal not available | :const:`secsgem.secs.data_items.ACKC10.TERMINAL_NOT_AVAILABLE` |
        +-------+------------------------+----------------------------------------------------------------+
        | 3-63  | Other error            |                                                                |
        +-------+------------------------+----------------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS10F02 <secsgem.secs.functions.SecsS10F02>`
        - :class:`SecsS10F04 <secsgem.secs.functions.SecsS10F04>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    NOT_DISPLAYED = 1
    TERMINAL_NOT_AVAILABLE = 2
