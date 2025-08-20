import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli import app as cli_app


def test_cmd_invokes_method(monkeypatch):
    class DummyRobot:
        def __init__(self):
            self.called = False
        def action(self):
            self.called = True

    cli_app._ACTIVE_DRIVERS['dummy1'] = DummyRobot()
    result = CliRunner().invoke(cli_app.app, ['cmd', 'dummy1', 'action'])

    assert result.exit_code == 0
    assert cli_app._ACTIVE_DRIVERS['dummy1'].called
    cli_app._ACTIVE_DRIVERS.clear()


def test_cmd_invalid_method(monkeypatch):
    class DummyRobot:
        pass

    cli_app._ACTIVE_DRIVERS['dummy2'] = DummyRobot()
    result = CliRunner().invoke(cli_app.app, ['cmd', 'dummy2', 'missing'])

    assert result.exit_code == 1
    cli_app._ACTIVE_DRIVERS.clear()


def test_cmd_invalid_alias():
    result = CliRunner().invoke(cli_app.app, ['cmd', 'ghost', 'dance'])
    assert result.exit_code == 1
