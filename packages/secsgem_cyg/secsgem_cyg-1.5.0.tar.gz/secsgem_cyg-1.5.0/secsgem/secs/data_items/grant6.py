"""GRANT6 data item."""
from .. import variables
from .base import DataItemBase


class GRANT6(DataItemBase):
    """Permission to send.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+----------------+--------------------------------------------------------+
        | Value | Description    | Constant                                               |
        +=======+================+========================================================+
        | 0     | Granted        | :const:`secsgem.secs.data_items.GRANT6.GRANTED`        |
        +-------+----------------+--------------------------------------------------------+
        | 1     | Busy           | :const:`secsgem.secs.data_items.GRANT6.BUSY`           |
        +-------+----------------+--------------------------------------------------------+
        | 2     | Not interested | :const:`secsgem.secs.data_items.GRANT6.NOT_INTERESTED` |
        +-------+----------------+--------------------------------------------------------+
        | 3-63  | Other error    |                                                        |
        +-------+----------------+--------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS06F06 <secsgem.secs.functions.SecsS06F06>`

    """

    __type__ = variables.Binary
    __count__ = 1

    GRANTED = 0
    BUSY = 1
    NOT_INTERESTED = 2
