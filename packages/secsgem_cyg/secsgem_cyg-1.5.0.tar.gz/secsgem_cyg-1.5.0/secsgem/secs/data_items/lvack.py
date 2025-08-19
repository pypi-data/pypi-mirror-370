"""LVACK data item."""
from .. import variables
from .base import DataItemBase


class LVACK(DataItemBase):
    """Acknowledgement code for variable limit.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------------+-----------------------------------------------------------+
        | Value | Description             | Constant                                                  |
        +=======+=========================+===========================================================+
        | 0     | OK                      | :const:`secsgem.secs.data_items.LVACK.OK`                 |
        +-------+-------------------------+-----------------------------------------------------------+
        | 1     | Variable does not exist | :const:`secsgem.secs.data_items.LVACK.VARIABLE_UNKNOWN`   |
        +-------+-------------------------+-----------------------------------------------------------+
        | 2     | Variable has no limits  | :const:`secsgem.secs.data_items.LVACK.NO_LIMITS`          |
        +-------+-------------------------+-----------------------------------------------------------+
        | 3     | Variable repeated       | :const:`secsgem.secs.data_items.LVACK.DUPLICATE_VARIABLE` |
        +-------+-------------------------+-----------------------------------------------------------+
        | 4     | Limit value error       | :const:`secsgem.secs.data_items.LVACK.LIMIT_ERROR`        |
        +-------+-------------------------+-----------------------------------------------------------+
        | 5-63  | Reserved                |                                                           |
        +-------+-------------------------+-----------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F46 <secsgem.secs.functions.SecsS02F46>`

    """

    __type__ = variables.Binary
    __count__ = 1

    OK = 0
    VARIABLE_UNKNOWN = 1
    NO_LIMITS = 2
    DUPLICATE_VARIABLE = 3
    LIMIT_ERROR = 4
