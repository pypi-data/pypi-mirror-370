"""Header for the hsms reject request."""

from .header import HsmsHeader, HsmsSType


class HsmsRejectReqHeader(HsmsHeader):
    """Header for Reject Request.

    Header for message with SType 7.
    """

    def __init__(self, system: int, s_type: HsmsSType, reason: int):
        """Initialize a hsms reject request.

        :param system: message ID
        :type system: integer
        :param s_type: s_type of rejected message
        :type s_type: integer
        :param reason: reason for rejection
        :type reason: integer

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsRejectReqHeader(17, secsgem.hsms.HsmsSType.DESELECT_REQ, 4)
            HsmsRejectReqHeader({session_id:0xffff, stream:03, function:04, p_type:0x00, s_type:0x07, \
system:0x00000011, require_response:False})
        """
        super().__init__(system, 0xFFFF, s_type.value, reason, False, 0x00, HsmsSType.REJECT_REQ)
