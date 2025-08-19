"""Data Value capability."""
from __future__ import annotations

import typing

from .capability import Capability
from .handler import GemHandler

if typing.TYPE_CHECKING:
    import secsgem.secs

    from .data_value import DataValue


class DataValueCapability(GemHandler, Capability):
    """Data Value capability on GEM equipment."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize capability."""
        super().__init__(*args, **kwargs)

        self.__data_values: dict[int | str, DataValue] = {
        }

    @property
    def _data_values(self) -> dict[int | str, DataValue]:
        """Get list of the data values.

        Returns:
            Data value list

        """
        return self.__data_values

    @property
    def data_values(self) -> dict[int | str, DataValue]:
        """Get list of the data values.

        Returns:
            Data value list

        """
        return self._data_values

    def on_dv_value_request(self,
                            data_value_id: secsgem.secs.variables.Base,
                            data_value: DataValue) -> secsgem.secs.variables.Base:
        """Get the data value depending on its configuation.

        Override in inherited class to provide custom data value request handling.

        Args:
            data_value_id: Id of the data value encoded in the corresponding type
            data_value: The data value requested

        Returns:
            The value encoded in the corresponding type

        """
        del data_value_id  # unused variable

        return data_value.value_type(data_value.value)

    def _get_dv_value(self, data_value: DataValue) -> secsgem.secs.variables.Base:
        """Get the data value depending on its configuation.

        Args:
            data_value: The data value requested

        Returns:
            The value encoded in the corresponding type

        """
        if data_value.use_callback:
            return self.on_dv_value_request(data_value.id_type(data_value.dvid), data_value)

        return data_value.value_type(data_value.value)
