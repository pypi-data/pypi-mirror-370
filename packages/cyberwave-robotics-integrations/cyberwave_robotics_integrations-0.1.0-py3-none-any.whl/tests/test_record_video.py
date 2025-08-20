import os
import sys

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli import app as cli_app


def test_record_video(monkeypatch, tmp_path):
    frames = [b'aa', b'bb']

    class DummyDriver:
        def connect(self):
            pass
        def disconnect(self):
            pass
        def start_video(self, handler=None):
            for f in frames:
                handler(f)
        def stop_video(self):
            pass

    monkeypatch.setattr(cli_app, 'Robot', lambda *a, **kw: DummyDriver())
    result = CliRunner().invoke(cli_app.app, ['record-video', 'tello', '--output', str(tmp_path/'out.bin'), '--duration', '0'])
    assert result.exit_code == 0
    assert (tmp_path/'out.bin').read_bytes() == b''.join(frames)
