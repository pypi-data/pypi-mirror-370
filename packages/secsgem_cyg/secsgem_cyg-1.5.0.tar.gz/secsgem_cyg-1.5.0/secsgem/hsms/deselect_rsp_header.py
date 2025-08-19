"""Header for the hsms deselect response."""

from .header import HsmsHeader, HsmsSType


class HsmsDeselectRspHeader(HsmsHeader):
    """Header for Deselect Response.

    Header for message with SType 4.
    """

    def __init__(self, system: int):
        """Initialize a hsms deslelct response.

        Args:
            system: message ID

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsDeselectRspHeader(1)
            HsmsDeselectRspHeader({session_id:0xffff, stream:00, function:00, p_type:0x00, s_type:0x04, \
system:0x00000001, require_response:False})

        """
        super().__init__(system, 0xFFFF, 0, 0, False, 0x00, HsmsSType.DESELECT_RSP)
