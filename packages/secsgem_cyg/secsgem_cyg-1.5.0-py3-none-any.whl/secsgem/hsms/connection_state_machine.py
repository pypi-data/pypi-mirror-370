"""State machine for connection state."""
from __future__ import annotations

import enum

import secsgem.common


class ConnectionState(enum.Enum):
    """States for connection state machine."""

    NOT_CONNECTED = 0
    CONNECTED = 1
    CONNECTED_NOT_SELECTED = 2
    CONNECTED_SELECTED = 3


class ConnectionStateMachine(secsgem.common.StateMachine):
    """Connection state machine."""

    def __init__(self) -> None:
        """Initialize state machine."""
        super().__init__()

        self.not_connected = secsgem.common.State(
            ConnectionState.NOT_CONNECTED,
            "NOT_CONNECTED",
            initial=True)
        self.connected = secsgem.common.State(
            ConnectionState.CONNECTED,
            "CONNECTED")
        self.connected_not_selected = secsgem.common.State(
            ConnectionState.CONNECTED_NOT_SELECTED,
            "CONNECTED_NOT_SELECTED",
            parent=self.connected)
        self.connected_selected = secsgem.common.State(
            ConnectionState.CONNECTED_SELECTED,
            "CONNECTED_SELECTED",
            parent=self.connected)

        # transition 1
        self._current_state: secsgem.common.State = self.not_connected

        self._transitions: list[secsgem.common.Transition] = [
            secsgem.common.Transition(
                "connect",
                self.not_connected,
                self.connected_not_selected),  # 2
            secsgem.common.Transition(
                "disconnect",
                [self.connected_not_selected, self.connected_selected],
                self.not_connected),  # 3
            secsgem.common.Transition(
                "select",
                self.connected_not_selected,
                self.connected_selected),  # 4
            secsgem.common.Transition(
                "deselect",
                self.connected_selected,
                self.connected_not_selected),  # 5
            secsgem.common.Transition(
                "timeoutT7",
                self.connected_not_selected,
                self.not_connected),  # 6
        ]

    def connect(self) -> None:
        """Perform connect transition."""
        self._perform_transition("connect")

    def disconnect(self) -> None:
        """Perform disconnect transition."""
        self._perform_transition("disconnect")

    def select(self) -> None:
        """Perform select transition."""
        self._perform_transition("select")

    def deselect(self) -> None:
        """Perform deselect transition."""
        self._perform_transition("deselect")
