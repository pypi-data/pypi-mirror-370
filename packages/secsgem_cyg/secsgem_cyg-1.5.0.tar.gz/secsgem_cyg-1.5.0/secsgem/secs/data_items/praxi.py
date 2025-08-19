"""PRAXI data item."""
from .. import variables
from .base import DataItemBase


class PRAXI(DataItemBase):
    """Process axis.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+----------------------------+--------------------------------------------------------+
        | Value | Description                | Constant                                               |
        +=======+============================+========================================================+
        | 0     | Rows, top, increasing      | :const:`secsgem.secs.data_items.PRAXI.ROWS_TOP_INCR`   |
        +-------+----------------------------+--------------------------------------------------------+
        | 1     | Rows, top, decreasing      | :const:`secsgem.secs.data_items.PRAXI.ROWS_TOP_DECR`   |
        +-------+----------------------------+--------------------------------------------------------+
        | 2     | Rows, bottom, increasing   | :const:`secsgem.secs.data_items.PRAXI.ROWS_BOT_INCR`   |
        +-------+----------------------------+--------------------------------------------------------+
        | 3     | Rows, bottom, decreasing   | :const:`secsgem.secs.data_items.PRAXI.ROWS_BOT_DECR`   |
        +-------+----------------------------+--------------------------------------------------------+
        | 4     | Columns, left, increasing  | :const:`secsgem.secs.data_items.PRAXI.COLS_LEFT_INCR`  |
        +-------+----------------------------+--------------------------------------------------------+
        | 5     | Columns, left, decreasing  | :const:`secsgem.secs.data_items.PRAXI.COLS_LEFT_DECR`  |
        +-------+----------------------------+--------------------------------------------------------+
        | 6     | Columns, right, increasing | :const:`secsgem.secs.data_items.PRAXI.COLS_RIGHT_INCR` |
        +-------+----------------------------+--------------------------------------------------------+
        | 7     | Columns, right, decreasing | :const:`secsgem.secs.data_items.PRAXI.COLS_RIGHT_DECR` |
        +-------+----------------------------+--------------------------------------------------------+
        | 8-63  | Error                      |                                                        |
        +-------+----------------------------+--------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS12F01 <secsgem.secs.functions.SecsS12F01>`
        - :class:`SecsS12F03 <secsgem.secs.functions.SecsS12F03>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ROWS_TOP_INCR = 0
    ROWS_TOP_DECR = 1
    ROWS_BOT_INCR = 2
    ROWS_BOT_DECR = 3
    COLS_LEFT_INCR = 4
    COLS_LEFT_DECR = 5
    COLS_RIGHT_INCR = 6
    COLS_RIGHT_DECR = 7
