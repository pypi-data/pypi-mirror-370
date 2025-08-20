import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.factory import Robot
from cyberwave_robotics_integrations.drivers.spot_driver import SpotDriver


def test_factory_loads_spot_driver():
    robot = Robot('spot')
    assert isinstance(robot, SpotDriver)
