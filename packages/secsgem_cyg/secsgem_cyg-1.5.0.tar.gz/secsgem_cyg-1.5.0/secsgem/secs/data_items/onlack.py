"""ONLACK data item."""
from .. import variables
from .base import DataItemBase


class ONLACK(DataItemBase):
    """Acknowledge code for ONLINE request.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+--------------------+-----------------------------------------------------+
        | Value | Description        | Constant                                            |
        +=======+====================+=====================================================+
        | 0     | ONLINE Accepted    | :const:`secsgem.secs.data_items.ONLACK.ACCEPTED`    |
        +-------+--------------------+-----------------------------------------------------+
        | 1     | ONLINE Not allowed | :const:`secsgem.secs.data_items.ONLACK.NOT_ALLOWED` |
        +-------+--------------------+-----------------------------------------------------+
        | 2     | Already ONLINE     | :const:`secsgem.secs.data_items.ONLACK.ALREADY_ON`  |
        +-------+--------------------+-----------------------------------------------------+
        | 3-63  | Reserved           |                                                     |
        +-------+--------------------+-----------------------------------------------------+

    **Used In Function**
        - :class:`SecsS01F18 <secsgem.secs.functions.SecsS01F18>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    NOT_ALLOWED = 1
    ALREADY_ON = 2
