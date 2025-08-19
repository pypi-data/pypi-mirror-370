"""OFLACK data item."""
from .. import variables
from .base import DataItemBase


class OFLACK(DataItemBase):
    """Acknowledge code for OFFLINE request.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+---------------------+---------------------------------------------+
        | Value | Description         | Constant                                    |
        +=======+=====================+=============================================+
        | 0     | OFFLINE Acknowledge | :const:`secsgem.secs.data_items.OFLACK.ACK` |
        +-------+---------------------+---------------------------------------------+
        | 1-63  | Reserved            |                                             |
        +-------+---------------------+---------------------------------------------+

    **Used In Function**
        - :class:`SecsS01F16 <secsgem.secs.functions.SecsS01F16>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
