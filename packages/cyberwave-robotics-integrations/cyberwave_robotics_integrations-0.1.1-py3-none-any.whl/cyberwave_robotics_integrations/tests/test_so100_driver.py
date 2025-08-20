import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.drivers.so100_driver import So100Driver


def test_so100_driver_connect_move_grip():
    driver = So100Driver()
    driver.connect()
    driver.move_to("home")
    driver.grip(True)
    driver.set_joint_positions([0, 0, 0, 0, 0, 0])
    status = driver.get_status()
    assert status["connected"] is True
    assert status["pose"] == "home"
    assert status["gripper"] == "open"
    assert status["joints"] == [0, 0, 0, 0, 0, 0]
    driver.execute_action("home")
    assert driver.get_joint_positions() == [0, 0, 0, 0, 0, 0]
    driver.disconnect()
