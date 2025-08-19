"""COMMACK data item."""
from .. import variables
from .base import DataItemBase


class COMMACK(DataItemBase):
    """Establish communications acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------+---------------------------------------------------+
        | Value | Description       | Constant                                          |
        +=======+===================+===================================================+
        | 0     | Accepted          | :const:`secsgem.secs.data_items.COMMACK.ACCEPTED` |
        +-------+-------------------+---------------------------------------------------+
        | 1     | Denied, Try Again | :const:`secsgem.secs.data_items.COMMACK.DENIED`   |
        +-------+-------------------+---------------------------------------------------+
        | 2-63  | Reserved          |                                                   |
        +-------+-------------------+---------------------------------------------------+

    **Used In Function**
        - :class:`SecsS01F14 <secsgem.secs.functions.SecsS01F14>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    DENIED = 1
