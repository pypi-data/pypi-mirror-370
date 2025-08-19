"""ALTX data item."""
from .. import variables
from .base import DataItemBase


class ALTX(DataItemBase):
    """Alarm text.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 120

    **Used In Function**
        - :class:`SecsS05F01 <secsgem.secs.functions.SecsS05F01>`
        - :class:`SecsS05F06 <secsgem.secs.functions.SecsS05F06>`
        - :class:`SecsS05F08 <secsgem.secs.functions.SecsS05F08>`

    """

    __type__ = variables.String
    __count__ = 120
