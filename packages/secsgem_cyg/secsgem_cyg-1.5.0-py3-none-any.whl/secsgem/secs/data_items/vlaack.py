"""VLAACK data item."""
from .. import variables
from .base import DataItemBase


class VLAACK(DataItemBase):
    """Variable limit attribute acknowledgement code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+--------------------------------------------+---------------------------------------------------------+
        | Value | Description                                | Constant                                                |
        +=======+============================================+=========================================================+
        | 0     | Acknowledgement, command will be performed | :const:`secsgem.secs.data_items.VLAACK.ACK`             |
        +-------+--------------------------------------------+---------------------------------------------------------+
        | 1     | Limit attribute definition error           | :const:`secsgem.secs.data_items.VLAACK.LIMIT_DEF_ERROR` |
        +-------+--------------------------------------------+---------------------------------------------------------+
        | 2     | Cannot perform now                         | :const:`secsgem.secs.data_items.VLAACK.NOT_NOW`         |
        +-------+--------------------------------------------+---------------------------------------------------------+
        | 3-63  | Reserved, equipment specific error         |                                                         |
        +-------+--------------------------------------------+---------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F46 <secsgem.secs.functions.SecsS02F46>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    LIMIT_DEF_ERROR = 1
    NOT_NOW = 2
