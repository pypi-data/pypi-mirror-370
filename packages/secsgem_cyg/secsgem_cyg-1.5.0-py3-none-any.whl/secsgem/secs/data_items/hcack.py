"""HCACK data item."""
from .. import variables
from .base import DataItemBase


class HCACK(DataItemBase):
    """Host command parameter acknowledge code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+--------------------------------+-------------------------------------------------------------+
        | Value | Description                    | Constant                                                    |
        +=======+================================+=============================================================+
        | 0     | Acknowledge                    | :const:`secsgem.secs.data_items.HCACK.ACK`                  |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 1     | Denied, invalid command        | :const:`secsgem.secs.data_items.HCACK.INVALID_COMMAND`      |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 2     | Denied, cannot perform now     | :const:`secsgem.secs.data_items.HCACK.CANT_PERFORM_NOW`     |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 3     | Denied, parameter invalid      | :const:`secsgem.secs.data_items.HCACK.PARAMETER_INVALID`    |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 4     | Acknowledge, will finish later | :const:`secsgem.secs.data_items.HCACK.ACK_FINISH_LATER`     |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 5     | Rejected, already in condition | :const:`secsgem.secs.data_items.HCACK.ALREADY_IN_CONDITION` |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 6     | No such object                 | :const:`secsgem.secs.data_items.HCACK.NO_OBJECT`            |
        +-------+--------------------------------+-------------------------------------------------------------+
        | 7-63  | Reserved                       |                                                             |
        +-------+--------------------------------+-------------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F42 <secsgem.secs.functions.SecsS02F42>`
        - :class:`SecsS02F50 <secsgem.secs.functions.SecsS02F50>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    INVALID_COMMAND = 1
    CANT_PERFORM_NOW = 2
    PARAMETER_INVALID = 3
    ACK_FINISH_LATER = 4
    ALREADY_IN_CONDITION = 5
    NO_OBJECT = 6
