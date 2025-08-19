"""CEPACK data item."""
from .. import variables
from .base import DataItemBase


class CEPACK(DataItemBase):
    """Command enhanced parameter acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`

    **Values**
        +-------+----------------------------+---------------------------------------------------------------+
        | Value | Description                | Constant                                                      |
        +=======+============================+===============================================================+
        | 0     | No error                   | :const:`secsgem.secs.data_items.CEPACK.NO_ERROR`              |
        +-------+----------------------------+---------------------------------------------------------------+
        | 1     | CPNAME name does not exist | :const:`secsgem.secs.data_items.CEPACK.CPNAME_UNKNOWN`        |
        +-------+----------------------------+---------------------------------------------------------------+
        | 2     | Illegal value for CEPVAL   | :const:`secsgem.secs.data_items.CEPACK.CEPVAL_ILLEGAL_VALUE`  |
        +-------+----------------------------+---------------------------------------------------------------+
        | 3     | Illegal format for CEPVAL  | :const:`secsgem.secs.data_items.CEPACK.CEPVAL_ILLEGAL_FORMAT` |
        +-------+----------------------------+---------------------------------------------------------------+
        | 4     | CPNAME not valid as used   | :const:`secsgem.secs.data_items.CEPACK.CPNAME_INVALID`        |
        +-------+----------------------------+---------------------------------------------------------------+
        | 5-63  | Reserved                   |                                                               |
        +-------+----------------------------+---------------------------------------------------------------+

    """

    __type__ = variables.Binary

    NO_ERROR = 0
    CPNAME_UNKNOWN = 1
    CEPVAL_ILLEGAL_VALUE = 2
    CEPVAL_ILLEGAL_FORMAT = 3
    CPNAME_INVALID = 4
