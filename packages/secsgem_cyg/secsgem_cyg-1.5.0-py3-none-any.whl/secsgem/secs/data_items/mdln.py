"""MDLN data item."""
from .. import variables
from .base import DataItemBase


class MDLN(DataItemBase):
    """Equipment model type.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 20

    **Used In Function**
        - :class:`SecsS01F02 <secsgem.secs.functions.SecsS01F02>`
        - :class:`SecsS01F13 <secsgem.secs.functions.SecsS01F13>`
        - :class:`SecsS01F14 <secsgem.secs.functions.SecsS01F14>`

    """

    __type__ = variables.String
    __count__ = 20
