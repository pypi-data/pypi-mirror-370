import sys
import os
import pytest

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.drivers.so_arm100_driver import SoArm100Driver


def test_so_arm100_driver_basic():
    driver = SoArm100Driver()
    # Connecting requires pyserial; ensure failure is handled gracefully
    with pytest.raises(RuntimeError):
        driver.connect()
    driver.set_joint_positions([1, 2, 3, 4, 5, 6])
    assert driver.get_joint_positions() == [1, 2, 3, 4, 5, 6]
