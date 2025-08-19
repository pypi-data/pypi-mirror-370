"""Header for the hsms separate request."""

from .header import HsmsHeader, HsmsSType


class HsmsSeparateReqHeader(HsmsHeader):
    """Header for Separate Request.

    Header for message with SType 9.
    """

    def __init__(self, system: int):
        """Initialize a hsms separate request header.

        :param system: message ID
        :type system: integer

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsSeparateReqHeader(17)
            HsmsSeparateReqHeader({session_id:0xffff, stream:00, function:00, p_type:0x00, s_type:0x09, \
system:0x00000011, require_response:False})
        """
        super().__init__(system, 0xFFFF, 0, 0, False, 0x00, HsmsSType.SEPARATE_REQ)
