"""SDACK data item."""
from .. import variables
from .base import DataItemBase


class SDACK(DataItemBase):
    """Map setup acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+---------------+--------------------------------------------+
        | Value | Description   | Constant                                   |
        +=======+===============+============================================+
        | 0     | Received Data | :const:`secsgem.secs.data_items.SDACK.ACK` |
        +-------+---------------+--------------------------------------------+
        | 1-63  | Error         |                                            |
        +-------+---------------+--------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F02 <secsgem.secs.functions.SecsS12F02>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
