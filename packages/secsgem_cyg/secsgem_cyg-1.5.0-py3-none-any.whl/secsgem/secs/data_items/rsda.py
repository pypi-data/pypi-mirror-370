"""RSDA data item."""
from .. import variables
from .base import DataItemBase


class RSDA(DataItemBase):
    """Request spooled data acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------------------------+------------------------------------------------------+
        | Value | Description                         | Constant                                             |
        +=======+=====================================+======================================================+
        | 0     | OK                                  | :const:`secsgem.secs.data_items.RSDA.ACK`            |
        +-------+-------------------------------------+------------------------------------------------------+
        | 1     | Denied, busy try later              | :const:`secsgem.secs.data_items.RSDA.DENIED_BUSY`    |
        +-------+-------------------------------------+------------------------------------------------------+
        | 2     | Denied, spooled data does not exist | :const:`secsgem.secs.data_items.RSDA.DENIED_NO_DATA` |
        +-------+-------------------------------------+------------------------------------------------------+
        | 3-63  | Reserved                            |                                                      |
        +-------+-------------------------------------+------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS06F24 <secsgem.secs.functions.SecsS06F24>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    DENIED_BUSY = 1
    DENIED_NO_DATA = 2
