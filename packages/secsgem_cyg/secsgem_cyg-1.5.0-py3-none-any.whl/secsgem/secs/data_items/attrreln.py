"""ATTRRELN data item."""
from .. import variables
from .base import DataItemBase


class ATTRRELN(DataItemBase):
    """Attribute relation to attribute of object.

    :Type: :class:`U1 <secsgem.secs.variables.U1>`

    **Values**
        +-------+-----------------------+------------------------------------------------------+
        | Value | Description           | Constant                                             |
        +=======+=======================+======================================================+
        | 0     | Equal to              | :const:`secsgem.secs.data_items.ATTRRELN.EQUAL`      |
        +-------+-----------------------+------------------------------------------------------+
        | 1     | Not equal to          | :const:`secsgem.secs.data_items.ATTRRELN.NOT_EQUAL`  |
        +-------+-----------------------+------------------------------------------------------+
        | 2     | Less than             | :const:`secsgem.secs.data_items.ATTRRELN.LESS`       |
        +-------+-----------------------+------------------------------------------------------+
        | 3     | Less than or equal to | :const:`secsgem.secs.data_items.ATTRRELN.LESS_EQUAL` |
        +-------+-----------------------+------------------------------------------------------+
        | 4     | More than             | :const:`secsgem.secs.data_items.ATTRRELN.MORE`       |
        +-------+-----------------------+------------------------------------------------------+
        | 5     | More than or equal to | :const:`secsgem.secs.data_items.ATTRRELN.MORE_EQUAL` |
        +-------+-----------------------+------------------------------------------------------+
        | 6     | Value present         | :const:`secsgem.secs.data_items.ATTRRELN.PRESENT`    |
        +-------+-----------------------+------------------------------------------------------+
        | 7     | Value absent          | :const:`secsgem.secs.data_items.ATTRRELN.ABSENT`     |
        +-------+-----------------------+------------------------------------------------------+
        | 8-63  | Error                 |                                                      |
        +-------+-----------------------+------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS14F01 <secsgem.secs.functions.SecsS14F01>`

    """

    __type__ = variables.U1

    EQUAL = 0
    NOT_EQUAL = 1
    LESS = 2
    LESS_EQUAL = 3
    MORE = 4
    MORE_EQUAL = 5
    PRESENT = 6
    ABSENT = 7
