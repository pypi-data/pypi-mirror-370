"""STRACK data item."""
from .. import variables
from .base import DataItemBase


class STRACK(DataItemBase):
    """Spool stream acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+------------------------------------+----------------------------------------------------------+
        | Value | Description                        | Constant                                                 |
        +=======+====================================+==========================================================+
        | 1     | Spooling not allowed for stream    | :const:`secsgem.secs.data_items.STRACK.NOT_ALLOWED`      |
        +-------+------------------------------------+----------------------------------------------------------+
        | 2     | Stream unknown                     | :const:`secsgem.secs.data_items.STRACK.STREAM_UNKNOWN`   |
        +-------+------------------------------------+----------------------------------------------------------+
        | 3     | Unknown function for stream        | :const:`secsgem.secs.data_items.STRACK.FUNCTION_UNKNOWN` |
        +-------+------------------------------------+----------------------------------------------------------+
        | 4     | Secondary function for this stream | :const:`secsgem.secs.data_items.STRACK.SECONDARY`        |
        +-------+------------------------------------+----------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F44 <secsgem.secs.functions.SecsS02F44>`

    """

    __type__ = variables.Binary
    __count__ = 1

    NOT_ALLOWED = 1
    STREAM_UNKNOWN = 2
    FUNCTION_UNKNOWN = 3
    SECONDARY = 4
