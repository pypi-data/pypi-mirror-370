from __future__ import annotations

"""Input controller abstractions for Cyberwave robots."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from .base_robot import RobotDriver


class BaseInputController(ABC):
    """Abstract interface for user input controllers."""

    def __init__(self, robot: Optional[RobotDriver] = None) -> None:
        self.robot = robot

    def attach(self, robot: RobotDriver) -> None:
        """Attach to the given robot driver."""
        self.robot = robot

    def detach(self) -> None:
        """Detach from the current robot driver."""
        self.robot = None

    @abstractmethod
    def handle_input(self, data: Any) -> None:
        """Process an input event and forward commands to the robot."""


