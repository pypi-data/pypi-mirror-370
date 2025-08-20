"""Example driver for the Boston Dynamics Spot robot."""
from cyberwave_robotics_integrations.base_robot import Quadruped
from cyberwave_robotics_integrations.registry import register


@register
class SpotDriver(Quadruped):
    """Simple example implementation of a quadruped driver."""

    form_factor = "quadruped"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self, *args, **kwargs) -> None:
        print("Connecting to Spot robot...")
        self.connected = True

    def disconnect(self) -> None:
        print("Disconnecting Spot robot...")
        self.connected = False

    def move_to(self, x: float, y: float) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        print(f"Spot walking to ({x}, {y})")

    def sit(self) -> None:
        if not self.connected:
            raise RuntimeError("Robot not connected")
        print("Spot is sitting down")

    @classmethod
    def supports(cls, asset) -> bool:
        rid = ((getattr(asset, "metadata", None) or {}).get("registry_id") or "").lower()
        name = (getattr(asset, "name", "") or "").lower()
        return "spot" in rid or "boston_dynamics/spot" in rid or "spot" in name
