"""HSMS Header for streams/functions."""

from .header import HsmsHeader, HsmsSType


class HsmsStreamFunctionHeader(HsmsHeader):
    """Header for SECS message.

    Header for message with SType 0.
    """

    def __init__(  # pylint: disable=too-many-arguments
            self,
            system: int,
            stream: int,
            function: int,
            require_response: bool,
            session_id: int):
        """Initialize a stream function secs header.

        Args:
            system: message ID
            stream: messages stream
            function: messages function
            require_response: is response expected from remote
            session_id: device / session ID

        Example:
            >>> import secsgem.hsms
            >>>
            >>> secsgem.hsms.HsmsStreamFunctionHeader(22, 1, 1, True, 100)
            HsmsStreamFunctionHeader({session_id:0x0064, stream:01, function:01, p_type:0x00, s_type:0x00, \
system:0x00000016, require_response:True})
        """
        super().__init__(system, session_id, stream, function, require_response, 0x00, HsmsSType.DATA_MESSAGE)
