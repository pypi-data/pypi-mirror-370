"""Header for the hsms deselect request."""

from .header import HsmsHeader, HsmsSType


class HsmsDeselectReqHeader(HsmsHeader):
    """Header for Deselect Request.

    Header for message with SType 3.
    """

    def __init__(self, system: int):
        """Initialize a hsms deselect request.

        Args:
            system: message ID

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsDeselectReqHeader(1)
            HsmsDeselectReqHeader({session_id:0xffff, stream:00, function:00, p_type:0x00, s_type:0x03, \
system:0x00000001, require_response:False})

        """
        super().__init__(system, 0xFFFF, 0, 0, False, 0x00, HsmsSType.DESELECT_REQ)
