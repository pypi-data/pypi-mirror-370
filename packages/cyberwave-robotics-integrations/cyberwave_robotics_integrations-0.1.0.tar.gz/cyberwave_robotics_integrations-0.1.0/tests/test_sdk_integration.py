import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from importlib import reload
if "cyberwave" in sys.modules and getattr(sys.modules["cyberwave"], "__file__", None) is None:
    del sys.modules["cyberwave"]
import cyberwave as cw
reload(cw)
from cyberwave import RobotDriver
from cyberwave_robotics_integrations.drivers.spot_driver import SpotDriver


def test_robot_driver_exposed_via_sdk():
    robot = RobotDriver('spot')
    assert isinstance(robot, SpotDriver)
