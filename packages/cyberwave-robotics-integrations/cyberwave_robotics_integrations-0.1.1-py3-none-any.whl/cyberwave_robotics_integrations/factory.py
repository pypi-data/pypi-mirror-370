"""Factory loader for robot drivers."""
import importlib
from .base_robot import BaseRobot


def Robot(name: str, *args, **kwargs) -> BaseRobot:
    """Instantiate a robot driver by name.

    Parameters
    ----------
    name: str
        The lowercase name of the robot driver (e.g. ``"spot"``).
    Returns
    -------
    BaseRobot
        The instantiated driver class.
    """
    canonical = name.replace("-", "_")
    module_name = f"cyberwave_robotics_integrations.drivers.{canonical}_driver"
    class_name = "".join(part.capitalize() for part in canonical.split("_")) + "Driver"
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise RuntimeError(f"No driver found for robot '{name}'") from e
    try:
        driver_cls = getattr(module, class_name)
    except AttributeError as e:
        raise RuntimeError(f"Driver class '{class_name}' not found in {module_name}") from e
    return driver_cls(*args, **kwargs)
