"""Header for the hsms select request."""

from .header import HsmsHeader, HsmsSType


class HsmsSelectReqHeader(HsmsHeader):
    """Header for Select Request.

    Header for message with SType 1.
    """

    def __init__(self, system: int):
        """Initialize a hsms select request.

        :param system: message ID
        :type system: integer

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsSelectReqHeader(14)
            HsmsSelectReqHeader({session_id:0xffff, stream:00, function:00, p_type:0x00, s_type:0x01, \
system:0x0000000e, require_response:False})
        """
        super().__init__(system, 0xFFFF, 0, 0, False, 0x00, HsmsSType.SELECT_REQ)
