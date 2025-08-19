"""ORLOC data item."""
from .. import variables
from .base import DataItemBase


class ORLOC(DataItemBase):
    """Origin location.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+---------------------+----------------------------------------------------+
        | Value | Description         | Constant                                           |
        +=======+=====================+====================================================+
        | 0     | Center die of wafer | :const:`secsgem.secs.data_items.ORLOC.CENTER_DIE`  |
        +-------+---------------------+----------------------------------------------------+
        | 1     | Upper right         | :const:`secsgem.secs.data_items.ORLOC.UPPER_RIGHT` |
        +-------+---------------------+----------------------------------------------------+
        | 2     | Upper left          | :const:`secsgem.secs.data_items.ORLOC.UPPER_LEFT`  |
        +-------+---------------------+----------------------------------------------------+
        | 3     | Lower left          | :const:`secsgem.secs.data_items.ORLOC.LOWER_LEFT`  |
        +-------+---------------------+----------------------------------------------------+
        | 4     | Lower right         | :const:`secsgem.secs.data_items.ORLOC.LOWER_RIGHT` |
        +-------+---------------------+----------------------------------------------------+
        | 5-63  | Reserved, error     |                                                    |
        +-------+---------------------+----------------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F01 <secsgem.secs.functions.SecsS12F01>`
        - :class:`SecsS12F03 <secsgem.secs.functions.SecsS12F03>`
        - :class:`SecsS12F04 <secsgem.secs.functions.SecsS12F04>`

    """

    __type__ = variables.Binary
    __count__ = 1

    CENTER_DIE = 0
    UPPER_RIGHT = 1
    UPPER_LEFT = 2
    LOWER_LEFT = 3
    LOWER_RIGHT = 4
