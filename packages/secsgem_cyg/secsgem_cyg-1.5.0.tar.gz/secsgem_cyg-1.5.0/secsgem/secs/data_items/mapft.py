"""MAPFT data item."""
from .. import variables
from .base import DataItemBase


class MAPFT(DataItemBase):
    """Map data format.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------+---------------------------------------------------+
        | Value | Description       | Constant                                          |
        +=======+===================+===================================================+
        | 0     | Row format        | :const:`secsgem.secs.data_items.MAPFT.ROW`        |
        +-------+-------------------+---------------------------------------------------+
        | 1     | Array format      | :const:`secsgem.secs.data_items.MAPFT.ARRAY`      |
        +-------+-------------------+---------------------------------------------------+
        | 2     | Coordinate format | :const:`secsgem.secs.data_items.MAPFT.COORDINATE` |
        +-------+-------------------+---------------------------------------------------+
        | 3-63  | Error             |                                                   |
        +-------+-------------------+---------------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F03 <secsgem.secs.functions.SecsS12F03>`
        - :class:`SecsS12F05 <secsgem.secs.functions.SecsS12F05>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ROW = 0
    ARRAY = 1
    COORDINATE = 2
