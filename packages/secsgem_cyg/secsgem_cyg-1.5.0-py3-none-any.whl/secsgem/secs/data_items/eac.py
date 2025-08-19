"""EAC data item."""
from .. import variables
from .base import DataItemBase


class EAC(DataItemBase):
    """Equipment acknowledge code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+---------------------------------+-------------------------------------------------------+
        | Value | Description                     | Constant                                              |
        +=======+=================================+=======================================================+
        | 0     | Acknowledge                     | :const:`secsgem.secs.data_items.EAC.ACK`              |
        +-------+---------------------------------+-------------------------------------------------------+
        | 1     | Denied, not all constants exist | :const:`secsgem.secs.data_items.EAC.INVALID_CONSTANT` |
        +-------+---------------------------------+-------------------------------------------------------+
        | 2     | Denied, busy                    | :const:`secsgem.secs.data_items.EAC.BUSY`             |
        +-------+---------------------------------+-------------------------------------------------------+
        | 3     | Denied, constant out of range   | :const:`secsgem.secs.data_items.EAC.OUT_OF_RANGE`     |
        +-------+---------------------------------+-------------------------------------------------------+
        | 4-63  | Reserved, equipment specific    |                                                       |
        +-------+---------------------------------+-------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F16 <secsgem.secs.functions.SecsS02F16>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    INVALID_CONSTANT = 1
    BUSY = 2
    OUT_OF_RANGE = 3
