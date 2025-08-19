"""Contains hsms message class."""
from __future__ import annotations

import secsgem.common

from .header import HsmsHeader


class HsmsBlock(secsgem.common.Block[HsmsHeader]):
    """Data block for SECS I."""

    header_type = HsmsHeader
    length_format = "L"
    checksum_format = ""


class HsmsMessage(secsgem.common.Message):
    """Class for hsms message.

    Contains all required data and functions.
    """

    block_size = -1
    block_type = HsmsBlock

    @property
    def header(self) -> HsmsHeader:
        """Get the header."""
        return self._blocks[0].header

    @property
    def data(self) -> bytes:
        """Get the data."""
        return self._blocks[0].data

    @property
    def complete(self) -> bool:
        """Check if the message is complete."""
        return True
