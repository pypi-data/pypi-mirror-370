"""MAPER data item."""
from .. import variables
from .base import DataItemBase


class MAPER(DataItemBase):
    """Map error.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+---------------+-----------------------------------------------------+
        | Value | Description   | Constant                                            |
        +=======+===============+=====================================================+
        | 0     | ID not found  | :const:`secsgem.secs.data_items.MAPER.ID_UNKNOWN`   |
        +-------+---------------+-----------------------------------------------------+
        | 1     | Invalid data  | :const:`secsgem.secs.data_items.MAPER.INVALID_DATA` |
        +-------+---------------+-----------------------------------------------------+
        | 2     | Format error  | :const:`secsgem.secs.data_items.MAPER.FORMAT_ERROR` |
        +-------+---------------+-----------------------------------------------------+
        | 3-63  | Invalid error |                                                     |
        +-------+---------------+-----------------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F19 <secsgem.secs.functions.SecsS12F19>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ID_UNKNOWN = 0
    INVALID_DATA = 1
    FORMAT_ERROR = 2
