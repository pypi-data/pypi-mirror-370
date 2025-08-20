"""Example driver for the SO100 robotic arm."""
from cyberwave_robotics_integrations.base_robot import ArmRobot
from cyberwave_robotics_integrations.registry import register


@register
class So100Driver(ArmRobot):
    """Simple mock implementation of the SO100 arm driver."""

    form_factor = "arm"
    JOINT_LIMITS = [(-180.0, 180.0) for _ in range(6)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, joint_limits=self.JOINT_LIMITS, **kwargs)
        self._pose = None
        self._gripper_open = False
        self._predefined_actions.update({
            "home": [0.0 for _ in range(6)],
        })

    def connect(self, *args, **kwargs) -> None:
        print("Connecting to SO100 arm...")
        self.connected = True

    def disconnect(self) -> None:
        print("Disconnecting SO100 arm...")
        self.connected = False

    def move_to(self, pose) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        self._pose = pose
        print(f"Moving SO100 arm to pose {pose}")

    def grip(self, open: bool) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        self._gripper_open = open
        action = "Opening" if open else "Closing"
        print(f"{action} gripper")

    def set_joint_positions(self, pos_list) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        super().set_joint_positions(pos_list)
        print(f"Setting joints to {self._joints}")

    def get_joint_positions(self) -> list:
        return super().get_joint_positions()

    def execute_action(self, name: str) -> None:
        super().execute_action(name)
        print(f"Executed action '{name}'")

    def get_status(self) -> dict:
        """Return basic telemetry about the arm."""
        data = super().get_status()
        data.update({
            "pose": self._pose,
            "gripper": "open" if self._gripper_open else "closed",
        })
        return data

    # Registry-based support predicate
    @classmethod
    def supports(cls, asset) -> bool:
        rid = ((getattr(asset, "metadata", None) or {}).get("registry_id") or "").lower()
        return rid.startswith("so/100") or "so100" in rid or "so-100" in rid
