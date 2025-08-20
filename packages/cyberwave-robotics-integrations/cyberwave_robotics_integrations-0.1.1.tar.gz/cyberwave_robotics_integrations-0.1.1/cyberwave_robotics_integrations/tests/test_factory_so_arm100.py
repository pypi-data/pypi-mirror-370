import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.factory import Robot
from cyberwave_robotics_integrations.drivers.so_arm100_driver import SoArm100Driver


def test_factory_loads_so_arm100_driver():
    robot = Robot('so-arm100')
    assert isinstance(robot, SoArm100Driver)
