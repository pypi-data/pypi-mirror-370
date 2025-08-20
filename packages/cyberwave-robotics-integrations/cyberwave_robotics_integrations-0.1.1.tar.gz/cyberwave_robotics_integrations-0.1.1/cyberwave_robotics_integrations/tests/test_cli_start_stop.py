import sys
import os
import time as pytime

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import site
for p in site.getsitepackages():
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
sys.modules.pop('typer', None)
sys.modules.pop('typer.testing', None)

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli import app as cli_app


def test_start_stop_lifecycle(monkeypatch):
    events = []

    class DummyDriver:
        def connect(self):
            events.append('connect')

        def disconnect(self):
            events.append('disconnect')

        def get_status(self):
            return {}

    monkeypatch.setattr(cli_app, 'Robot', lambda *a, **kw: DummyDriver())
    monkeypatch.setattr(cli_app.time, 'sleep', lambda x: None)

    runner = CliRunner()
    start_result = runner.invoke(cli_app.app, ['start', 'tello', '--no-persistent'])
    pytime.sleep(0.05)
    result = runner.invoke(cli_app.app, ['stop', 'tello'])

    assert start_result.exit_code == 0
    assert result.exit_code == 0
    assert events == ['connect', 'disconnect']
    assert cli_app._ACTIVE_DRIVERS == {}


def test_stop_ambiguous_alias(monkeypatch):
    class SpotDriver:
        def connect(self):
            pass
        def disconnect(self):
            pass
        def get_status(self):
            return {}

    monkeypatch.setattr(cli_app, 'Robot', lambda *a, **kw: SpotDriver())
    monkeypatch.setattr(cli_app.time, 'sleep', lambda x: None)

    runner = CliRunner()
    runner.invoke(cli_app.app, ['start', 'spot', '--alias', 'spot-1', '--no-persistent'])
    runner.invoke(cli_app.app, ['start', 'spot', '--alias', 'spot-2', '--no-persistent'])
    pytime.sleep(0.05)
    result = runner.invoke(cli_app.app, ['stop', 'spot'])

    assert result.exit_code == 0
    assert "Multiple robots match 'spot'" in result.stdout
    assert set(cli_app._ACTIVE_DRIVERS.keys()) == {"spot-1", "spot-2"}

    runner.invoke(cli_app.app, ['stop', 'spot-1'])
    runner.invoke(cli_app.app, ['stop', 'spot-2'])
