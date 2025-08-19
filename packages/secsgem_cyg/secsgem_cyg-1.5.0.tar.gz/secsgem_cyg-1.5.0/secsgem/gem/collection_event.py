"""Wrapper for GEM collection event."""
from __future__ import annotations

import enum

import secsgem.secs.variables


class CollectionEventId(enum.Enum):
    """Default IDs for collection events."""
    EQUIPMENT_OFFLINE = 1
    CONTROL_STATE_LOCAL = 2
    CONTROL_STATE_REMOTE = 3
    CMD_START_DONE = 20
    CMD_STOP_DONE = 21


class CollectionEvent:  # pylint: disable=too-few-public-methods
    """Collection event definition."""

    def __init__(self,
                 ceid: int | str | CollectionEventId,
                 name: str,
                 data_values: list[int | str],
                 **kwargs):
        """Initialize a collection event.

        You can manually set the secs-type of the id with the 'id_type' keyword argument.

        Custom parameters can be set with the keyword arguments,
        they will be passed to the GemEquipmentHandlers callback
        :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_dv_value_request`.

        If use_callbacks is disabled, you can set the value with the value property.

        Args:
            ceid: ID of the collection event
            name: long name of the collection event
            data_values: data values available for this event
            **kwargs: additional attributes for object

        """
        self.ceid = ceid if not isinstance(ceid, CollectionEventId) else ceid.value
        self.name = name
        self.data_values = data_values

        self.id_type: type[secsgem.secs.variables.Base]

        if isinstance(self.ceid, int):
            self.id_type = secsgem.secs.variables.U4
        else:
            self.id_type = secsgem.secs.variables.String

        for key, value in kwargs.items():
            setattr(self, key, value)
