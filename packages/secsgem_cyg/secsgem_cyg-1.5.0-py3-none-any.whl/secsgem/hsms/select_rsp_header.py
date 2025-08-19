"""Header for the hsms select response."""

from .header import HsmsHeader, HsmsSType


class HsmsSelectRspHeader(HsmsHeader):
    """Header for Select Response.

    Header for message with SType 2.
    """

    def __init__(self, system: int):
        """Initialize a hsms select response.

        :param system: message ID
        :type system: integer

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsSelectRspHeader(24)
            HsmsSelectRspHeader({session_id:0xffff, stream:00, function:00, p_type:0x00, s_type:0x02, \
system:0x00000018, require_response:False})
        """
        super().__init__(system, 0xFFFF, 0, 0, False, 0x00, HsmsSType.SELECT_RSP)
