"""ACKC5 data item."""
from .. import variables
from .base import DataItemBase


class ACKC5(DataItemBase):
    """Acknowledge code for stream 5.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------+-------------------------------------------------+
        | Value | Description | Constant                                        |
        +=======+=============+=================================================+
        | 0     | Accepted    | :const:`secsgem.secs.data_items.ACKC5.ACCEPTED` |
        +-------+-------------+-------------------------------------------------+
        | 1-63  | Error       | :const:`secsgem.secs.data_items.ACKC5.ERROR`    |
        +-------+-------------+-------------------------------------------------+

    **Used In Function**
        - :class:`SecsS05F02 <secsgem.secs.functions.SecsS05F02>`
        - :class:`SecsS05F04 <secsgem.secs.functions.SecsS05F04>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    ERROR = 1
