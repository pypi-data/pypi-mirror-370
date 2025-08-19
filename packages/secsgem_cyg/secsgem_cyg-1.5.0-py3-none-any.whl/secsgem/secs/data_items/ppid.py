"""PPID data item."""
from .. import variables
from .base import DataItemBase


class PPID(DataItemBase):
    """Process program ID.

    :Types:
       - :class:`String <secsgem.secs.variables.String>`
       - :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 120

    **Used In Function**
        - :class:`SecsS07F01 <secsgem.secs.functions.SecsS07F01>`
        - :class:`SecsS07F03 <secsgem.secs.functions.SecsS07F03>`
        - :class:`SecsS07F05 <secsgem.secs.functions.SecsS07F05>`
        - :class:`SecsS07F06 <secsgem.secs.functions.SecsS07F06>`
        - :class:`SecsS07F17 <secsgem.secs.functions.SecsS07F17>`
        - :class:`SecsS07F20 <secsgem.secs.functions.SecsS07F20>`
        - :class:`SecsS07F25 <secsgem.secs.functions.SecsS07F25>`

    """

    __type__ = variables.Dynamic
    __allowedtypes__ = [
        variables.String,
        variables.Binary
    ]
    __count__ = 120
