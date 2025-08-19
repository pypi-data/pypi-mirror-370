"""CAACK data item."""
from .. import variables
from .base import DataItemBase


class CAACK(DataItemBase):
    """Carrier Action Request acknowledge code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+------------------------+-------------------------------------------------------------+
        | Value | Description            | Constant                                                    |
        +=======+========================+=============================================================+
        | 0     | Accepted               | :const:`secsgem.secs.data_items.CAACK.ACCEPTED`             |
        +-------+------------------------+-------------------------------------------------------------+
    """

    __type__ = variables.U1
    __count__ = 1

    ACCEPTED = 0
