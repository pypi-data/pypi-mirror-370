"""ALED data item."""
from .. import variables
from .base import DataItemBase


class ALED(DataItemBase):
    """Alarm en-/disable code byte.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +---------+-------------+-----------------------------------------------+
        | Value   | Description | Constant                                      |
        +=========+=============+===============================================+
        | 0       | Disable     | :const:`secsgem.secs.data_items.ALED.DISABLE` |
        +---------+-------------+-----------------------------------------------+
        | 1-127   | Not used    |                                               |
        +---------+-------------+-----------------------------------------------+
        | 128     | Enable      | :const:`secsgem.secs.data_items.ALED.ENABLE`  |
        +---------+-------------+-----------------------------------------------+
        | 129-255 | Not used    |                                               |
        +---------+-------------+-----------------------------------------------+

    **Used In Function**
        - :class:`SecsS05F03 <secsgem.secs.functions.SecsS05F03>`

    """

    __type__ = variables.Binary
    __count__ = 1

    DISABLE = 0
    ENABLE = 128
