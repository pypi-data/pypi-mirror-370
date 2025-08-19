"""DRACK data item."""
from .. import variables
from .base import DataItemBase


class DRACK(DataItemBase):
    """Define report acknowledge code.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------------------+-----------------------------------------------------------+
        | Value | Description                   | Constant                                                  |
        +=======+===============================+===========================================================+
        | 0     | Acknowledge                   | :const:`secsgem.secs.data_items.DRACK.ACK`                |
        +-------+-------------------------------+-----------------------------------------------------------+
        | 1     | Denied, insufficient space    | :const:`secsgem.secs.data_items.DRACK.INSUFFICIENT_SPACE` |
        +-------+-------------------------------+-----------------------------------------------------------+
        | 2     | Denied, invalid format        | :const:`secsgem.secs.data_items.DRACK.INVALID_FORMAT`     |
        +-------+-------------------------------+-----------------------------------------------------------+
        | 3     | Denied, RPTID already defined | :const:`secsgem.secs.data_items.DRACK.RPTID_REDEFINED`    |
        +-------+-------------------------------+-----------------------------------------------------------+
        | 4     | Denied, VID doesn't exist     | :const:`secsgem.secs.data_items.DRACK.VID_UNKNOWN`        |
        +-------+-------------------------------+-----------------------------------------------------------+
        | 5-63  | Reserved, other errors        |                                                           |
        +-------+-------------------------------+-----------------------------------------------------------+

    **Used In Function**
        - :class:`SecsS02F34 <secsgem.secs.functions.SecsS02F34>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACK = 0
    INSUFFICIENT_SPACE = 1
    INVALID_FORMAT = 2
    RPTID_REDEFINED = 3
    VID_UNKNOWN = 4
