import sys
import os
import time as pytime
import types

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Ensure the real Typer package is used instead of the local stub
import site
for p in site.getsitepackages():
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
sys.modules.pop('typer', None)
sys.modules.pop('typer.testing', None)

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli import app as cli_app


def test_auto_register(monkeypatch):
    events = []

    class DummyDriver:
        def connect(self):
            events.append("connect")
        def disconnect(self):
            events.append("disconnect")
        def get_status(self):
            return {}

    class DummyClient:
        def __init__(self, *a, **kw):
            pass
        async def register_device(self, project_id, name, device_type, asset_catalog_uuid=None):
            events.append(("register", project_id, name, device_type, asset_catalog_uuid))
            return {"id": 99}
        async def send_telemetry(self, device_id, telemetry):
            events.append(("telemetry", device_id))

    config_mod = types.SimpleNamespace(DEFAULT_PROJECT=123)
    monkeypatch.setitem(sys.modules, "cyberwave_cli.config", config_mod)

    monkeypatch.setattr(cli_app, "Robot", lambda *a, **kw: DummyDriver())
    monkeypatch.setattr(cli_app, "Client", DummyClient)
    monkeypatch.setattr(cli_app.time, "sleep", lambda x: None)
    monkeypatch.setattr(cli_app.webbrowser, "open", lambda url: events.append(("open", url)))

    runner = CliRunner()
    start_result = runner.invoke(cli_app.app, ["start", "tello", "--no-persistent"])
    pytime.sleep(0.05)
    runner.invoke(cli_app.app, ["stop", "tello"])

    assert start_result.exit_code == 0
    assert ("register", 123, "tello", "tello", None) in events
    assert ("open", f"https://.../projects/123/devices/99") in events
