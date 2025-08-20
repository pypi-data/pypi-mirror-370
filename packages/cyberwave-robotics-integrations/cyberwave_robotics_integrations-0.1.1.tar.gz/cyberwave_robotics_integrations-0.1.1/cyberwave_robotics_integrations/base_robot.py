from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

class BaseRobot(ABC):
    """Abstract base class for all robot drivers."""

    form_factor: str

    @abstractmethod
    def connect(self, *args, **kwargs) -> None:
        """Connect to the robot."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the robot."""

    def execute_task(self, task: str) -> None:
        """Default implementation for executing a high level task."""
        print(f"Executing task '{task}' on {self.form_factor} robot...")


class RobotDriver(BaseRobot, ABC):
    """Base driver with generic connection state helpers."""

    def __init__(self, *args, **kwargs) -> None:
        self.connected = False

    def get_status(self) -> Dict[str, object]:
        """Return generic connectivity information."""
        return {"connected": self.connected}

class FlyingDrone(RobotDriver, ABC):
    """Base class for aerial robots."""

    form_factor = "drone"

    @abstractmethod
    def takeoff(self) -> None:
        """Command the drone to take off."""

    @abstractmethod
    def land(self) -> None:
        """Command the drone to land."""

class ArmRobot(RobotDriver, ABC):
    """Base class for robotic arms."""

    form_factor = "arm"

    @abstractmethod
    def move_to(self, pose) -> None:
        """Move the arm to the specified pose."""

    @abstractmethod
    def grip(self, open: bool) -> None:
        """Open or close the gripper."""

    joint_limits: List[Tuple[float, float]] = []

    def __init__(self, *args, joint_limits: List[Tuple[float, float]] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.joint_limits = joint_limits or self.joint_limits
        self._joints: List[float] = [0.0 for _ in self.joint_limits]
        self._predefined_actions: Dict[str, List[float]] = {}

    def execute_action(self, name: str) -> None:
        if name not in self._predefined_actions:
            raise ValueError(f"Unknown action '{name}'")
        self.set_joint_positions(self._predefined_actions[name])

    def set_joint_positions(self, pos_list: List[float]) -> None:
        if self.joint_limits and len(pos_list) != len(self.joint_limits):
            raise ValueError("Invalid joint list length")
        if not self.joint_limits:
            self._joints = list(map(float, pos_list))
            return
        clamped = []
        for val, (jmin, jmax) in zip(pos_list, self.joint_limits):
            val = max(min(float(val), jmax), jmin)
            clamped.append(val)
        self._joints = clamped

    def get_joint_positions(self) -> List[float]:
        return list(self._joints)

    def get_status(self) -> Dict[str, object]:
        data = super().get_status()
        data["joints"] = self.get_joint_positions()
        return data

class Quadruped(RobotDriver, ABC):
    """Base class for legged robots with four legs."""

    form_factor = "quadruped"

    @abstractmethod
    def move_to(self, x: float, y: float) -> None:
        """Walk to the specified coordinates."""

    @abstractmethod
    def sit(self) -> None:
        """Command the robot to sit down."""
