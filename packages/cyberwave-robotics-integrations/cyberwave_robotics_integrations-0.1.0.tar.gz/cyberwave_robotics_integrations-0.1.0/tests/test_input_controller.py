import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.input_controller import BaseInputController
from cyberwave_robotics_integrations.drivers.so100_driver import So100Driver


class DummyController(BaseInputController):
    def handle_input(self, data):
        if self.robot is None:
            return
        if data.get("action") == "move":
            self.robot.set_joint_positions(data.get("joints", []))


def test_controller_attaches_and_moves():
    robot = So100Driver()
    robot.connect()
    ctrl = DummyController(robot)
    ctrl.handle_input({"action": "move", "joints": [1, 2, 3, 4, 5, 6]})
    assert robot.get_joint_positions() == [1, 2, 3, 4, 5, 6]
    ctrl.detach()
    ctrl.handle_input({"action": "move", "joints": [0, 0, 0, 0, 0, 0]})
    # Should remain unchanged after detach
    assert robot.get_joint_positions() == [1, 2, 3, 4, 5, 6]
    robot.disconnect()
