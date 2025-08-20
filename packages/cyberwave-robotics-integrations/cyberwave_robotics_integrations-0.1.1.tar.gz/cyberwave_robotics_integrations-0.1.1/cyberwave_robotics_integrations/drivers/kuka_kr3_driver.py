"""Example driver for the KUKA KR3 robotic arm."""
from cyberwave_robotics_integrations.base_robot import ArmRobot


class KukaKR3Driver(ArmRobot):
    """Simple example implementation of an arm driver."""

    form_factor = "arm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, joint_limits=[], **kwargs)

    def connect(self, *args, **kwargs) -> None:
        print("Connecting to KUKA KR3 arm...")
        self.connected = True

    def disconnect(self) -> None:
        print("Disconnecting KUKA KR3 arm...")
        self.connected = False

    def move_to(self, pose) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        print(f"Moving KR3 arm to pose {pose}")

    def grip(self, open: bool) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        action = "Opening" if open else "Closing"
        print(f"{action} gripper")
