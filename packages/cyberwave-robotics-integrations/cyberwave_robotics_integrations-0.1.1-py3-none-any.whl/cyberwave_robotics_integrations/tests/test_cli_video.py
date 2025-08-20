import sys
import os
import time as pytime

from typer.testing import CliRunner
from cyberwave_robotics_integrations.cli import app as cli_app


def test_start_stop_with_video(monkeypatch):
    events = []

    class DummyDriver:
        def connect(self):
            events.append("connect")
        def start_video(self):
            events.append("start_video")
        def stop_video(self):
            events.append("stop_video")
        def disconnect(self):
            events.append("disconnect")
        def get_status(self):
            return {}

    monkeypatch.setattr(cli_app, "Robot", lambda *a, **kw: DummyDriver())
    monkeypatch.setattr(cli_app.time, "sleep", lambda x: None)

    runner = CliRunner()
    start_result = runner.invoke(cli_app.app, ["start", "tello", "--video", "--no-persistent"])
    pytime.sleep(0.05)
    runner.invoke(cli_app.app, ["stop", "tello", "--video"])

    assert start_result.exit_code == 0
    assert set(events) == {"connect", "start_video", "stop_video", "disconnect"}


def test_video_frames_uploaded(monkeypatch):
    frames = [b"a", b"b"]

    class DummyDriver:
        def connect(self):
            pass
        def start_video(self, handler=None):
            for f in frames:
                if handler:
                    handler(f)
        def stop_video(self):
            pass
        def disconnect(self):
            pass
        def get_status(self):
            return {}

    uploaded = []

    class DummyClient:
        def __init__(self, *a, **kw):
            pass
        async def upload_video_frame(self, device_id, frame_bytes):
            uploaded.append(frame_bytes)
        async def send_telemetry(self, device_id, telemetry):
            pass

    monkeypatch.setattr(cli_app, "Robot", lambda *a, **kw: DummyDriver())
    monkeypatch.setattr(cli_app, "Client", DummyClient)
    monkeypatch.setattr(cli_app.time, "sleep", lambda x: None)

    runner = CliRunner()
    start_result = runner.invoke(cli_app.app, ["start", "tello", "--video", "--device-id", "1", "--no-persistent"])
    pytime.sleep(0.05)
    runner.invoke(cli_app.app, ["stop", "tello", "--video"])

    assert start_result.exit_code == 0
    assert uploaded == frames
