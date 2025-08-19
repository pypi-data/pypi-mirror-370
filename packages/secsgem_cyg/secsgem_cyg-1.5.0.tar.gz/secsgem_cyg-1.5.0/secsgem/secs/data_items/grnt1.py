"""GRNT1 data item."""
from .. import variables
from .base import DataItemBase


class GRNT1(DataItemBase):
    """Grant code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-----------------------+-----------------------------------------------------------+
        | Value | Description           | Constant                                                  |
        +=======+=======================+===========================================================+
        | 0     | Acknowledge           | :const:`secsgem.secs.data_items.GRNT1.ACK`                |
        +-------+-----------------------+-----------------------------------------------------------+
        | 1     | Busy, try again       | :const:`secsgem.secs.data_items.GRNT1.BUSY`               |
        +-------+-----------------------+-----------------------------------------------------------+
        | 2     | No space              | :const:`secsgem.secs.data_items.GRNT1.NO_SPACE`           |
        +-------+-----------------------+-----------------------------------------------------------+
        | 3     | Map too large         | :const:`secsgem.secs.data_items.GRNT1.MAP_TOO_LARGE`      |
        +-------+-----------------------+-----------------------------------------------------------+
        | 4     | Duplicate ID          | :const:`secsgem.secs.data_items.GRNT1.DUPLICATE_ID`       |
        +-------+-----------------------+-----------------------------------------------------------+
        | 5     | Material ID not found | :const:`secsgem.secs.data_items.GRNT1.MATERIALID_UNKNOWN` |
        +-------+-----------------------+-----------------------------------------------------------+
        | 6     | Unknown map format    | :const:`secsgem.secs.data_items.GRNT1.UNKNOWN_MAP_FORMAT` |
        +-------+-----------------------+-----------------------------------------------------------+
        | 7-63  | Reserved, error       |                                                           |
        +-------+-----------------------+-----------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F06 <secsgem.secs.functions.SecsS12F06>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    BUSY = 1
    NO_SPACE = 2
    MAP_TOO_LARGE = 3
    DUPLICATE_ID = 4
    MATERIALID_UNKNOWN = 5
    UNKNOWN_MAP_FORMAT = 6
