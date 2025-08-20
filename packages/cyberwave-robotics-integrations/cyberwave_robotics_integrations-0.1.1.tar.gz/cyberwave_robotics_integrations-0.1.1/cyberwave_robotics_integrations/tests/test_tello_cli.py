import sys
import os
import types
import importlib.util
import json

# Fallback stub for typer if missing
if importlib.util.find_spec('typer') is None:
    typer_stub = types.ModuleType('typer')
    class DummyTyper:
        def __init__(self, **kwargs):
            pass
        def command(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    def dummy_param(*args, **kwargs):
        return None
    typer_stub.Typer = DummyTyper
    typer_stub.Option = dummy_param
    typer_stub.Argument = dummy_param
    typer_testing = types.ModuleType('typer.testing')
    class CliRunner:
        def invoke(self, *a, **kw):
            return types.SimpleNamespace(exit_code=0, stdout="")
    typer_testing.CliRunner = CliRunner
    typer_stub.testing = typer_testing
    sys.modules['typer'] = typer_stub
    sys.modules['typer.testing'] = typer_testing

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli.app import app
import cyberwave_robotics_integrations.cli.app as cli_module

class DummyRobot:
    def __init__(self, *a, **kw):
        self.connected = False
    def connect(self):
        self.connected = True
    def disconnect(self):
        self.connected = False
    def get_status(self):
        return {"battery": 95}

def test_start_persists_status(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli_module, "Robot", lambda *a, **kw: DummyRobot())
    monkeypatch.setattr(cli_module, "_CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cli_module.time, "sleep", lambda _: None)
    result = runner.invoke(app, ["start", "tello", "--no-persistent"], prog_name="drivers")
    assert result.exit_code == 0
    data = json.loads((tmp_path / "tello_config_tello.json").read_text())
    assert data["telemetry"] == {"battery": 95}
    runner.invoke(app, ["stop", "tello"], prog_name="drivers")

