"""ACKC6 data item."""
from .. import variables
from .base import DataItemBase


class ACKC6(DataItemBase):
    """Acknowledge code for stream 6.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------+-------------------------------------------------+
        | Value | Description | Constant                                        |
        +=======+=============+=================================================+
        | 0     | Accepted    | :const:`secsgem.secs.data_items.ACKC6.ACCEPTED` |
        +-------+-------------+-------------------------------------------------+
        | 1-63  | Error       | :const:`secsgem.secs.data_items.ACKC6.ERROR`    |
        +-------+-------------+-------------------------------------------------+

    **Used In Function**
        - :class:`SecsS06F02 <secsgem.secs.functions.SecsS06F02>`
        - :class:`SecsS06F12 <secsgem.secs.functions.SecsS06F12>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    ERROR = 1
