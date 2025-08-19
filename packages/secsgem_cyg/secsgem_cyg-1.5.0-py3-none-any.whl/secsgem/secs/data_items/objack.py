"""OBJACK data item."""
from .. import variables
from .base import DataItemBase


class OBJACK(DataItemBase):
    """Object acknowledgement code.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`
    :Length: 1

    **Values**
        +-------+-------------+----------------------------------------------------+
        | Value | Description | Constant                                           |
        +=======+=============+====================================================+
        | 0     | Successful  | :const:`secsgem.secs.data_items.OBJACK.SUCCESSFUL` |
        +-------+-------------+----------------------------------------------------+
        | 1     | Error       | :const:`secsgem.secs.data_items.OBJACK.ERROR`      |
        +-------+-------------+----------------------------------------------------+
        | 2-63  | Reserved    |                                                    |
        +-------+-------------+----------------------------------------------------+

    **Used In Function**
        - :class:`SecsS14F02 <secsgem.secs.functions.SecsS14F02>`
        - :class:`SecsS14F04 <secsgem.secs.functions.SecsS14F04>`

    """

    __type__ = variables.U1
    __count__ = 1

    SUCCESSFUL = 0
    ERROR = 1
