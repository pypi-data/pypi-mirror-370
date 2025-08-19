"""ERACK data item."""
from .. import variables
from .base import DataItemBase


class ERACK(DataItemBase):
    """Enable/disable event report acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+----------------------------+-----------------------------------------------------+
        | Value | Description                | Constant                                            |
        +=======+============================+=====================================================+
        | 0     | Accepted                   | :const:`secsgem.secs.data_items.ERACK.ACCEPTED`     |
        +-------+----------------------------+-----------------------------------------------------+
        | 1     | Denied, CEID doesn't exist | :const:`secsgem.secs.data_items.ERACK.CEID_UNKNOWN` |
        +-------+----------------------------+-----------------------------------------------------+
        | 2-63  | Reserved                   |                                                     |
        +-------+----------------------------+-----------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F38 <secsgem.secs.functions.SecsS02F38>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    CEID_UNKNOWN = 1
