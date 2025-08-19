"""Helper to track block send result across threads."""
from __future__ import annotations

import enum
import threading


class BlockSendResult(enum.Enum):
    """Enum for send result including not send state."""

    NOT_SENT = 0
    SENT_OK = 1
    SENT_ERROR = 2


class BlockSendInfo:
    """Container for sending block and waiting for result."""

    def __init__(self, data: bytes):
        """Initialize block send info object.

        Args:
            data: data to send.

        """
        self._data = data

        self._result = BlockSendResult.NOT_SENT
        self._result_trigger = threading.Event()

    @property
    def data(self) -> bytes:
        """Get the data for sending."""
        return self._data

    def resolve(self, result: bool):
        """Resolve the send data with a result.

        Args:
            result: result to resolve with

        """
        self._result = BlockSendResult.SENT_OK if result else BlockSendResult.SENT_ERROR
        self._result_trigger.set()

    def wait(self) -> bool:
        """Wait for the message is sent and a result is available."""
        self._result_trigger.wait()

        return self._result == BlockSendResult.SENT_OK
