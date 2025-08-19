"""Clock capability."""
from __future__ import annotations

import datetime

from dateutil.tz import tzlocal

from .capability import Capability
from .handler import GemHandler


class ClockCapability(GemHandler, Capability):
    """Clock capability on GEM equipment."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize capability."""
        super().__init__(*args, **kwargs)

        self.__time_format = 1

    @property
    def _time_format(self) -> int:
        return self.__time_format

    @_time_format.setter
    def _time_format(self, value: int):
        self.__time_format = value

    def _get_clock(self) -> str:
        """Get the clock depending on configured time format.

        Returns:
            time code

        """
        now = datetime.datetime.now(tzlocal())
        if self._time_format == 0:
            return now.strftime("%y%m%d%H%M%S")

        if self._time_format == 2:
            return now.isoformat()

        return now.strftime("%Y%m%d%H%M%S") + now.strftime("%f")[0:2]
