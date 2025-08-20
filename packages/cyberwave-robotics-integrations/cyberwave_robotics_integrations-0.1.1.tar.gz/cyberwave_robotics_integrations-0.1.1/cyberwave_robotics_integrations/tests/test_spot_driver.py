import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.drivers.spot_driver import SpotDriver


def test_spot_driver_connect_move_sit():
    driver = SpotDriver()
    driver.connect()
    driver.move_to(1.0, 2.0)
    driver.sit()
    driver.disconnect()
