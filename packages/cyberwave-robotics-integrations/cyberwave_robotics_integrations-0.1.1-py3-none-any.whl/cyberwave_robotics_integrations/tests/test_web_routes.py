import sys
import os
import importlib.util
import pytest

pytest.importorskip("flask")

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from cyberwave_robotics_integrations.web import create_app
import cyberwave_robotics_integrations.cli.app as cli_app


class DummyRobot:
    def get_status(self):
        return {"bat": 100}


def setup_module(module):
    cli_app._ACTIVE_DRIVERS["dummy"] = DummyRobot()


def teardown_module(module):
    cli_app._ACTIVE_DRIVERS.clear()


def test_index_route():
    app = create_app()
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200


def test_telemetry_route():
    app = create_app()
    client = app.test_client()
    res = client.get("/robot/dummy/telemetry")
    assert res.status_code == 200
    assert res.get_json() == {"bat": 100}


class DummyActionRobot:
    def __init__(self):
        self.action_executed = False

    def dance(self):
        self.action_executed = True


def test_command_route_calls_driver_method():
    app = create_app()
    client = app.test_client()
    cli_app._ACTIVE_DRIVERS["dummy_action"] = DummyActionRobot()
    res = client.post("/robot/dummy_action/command/dance")
    assert res.status_code == 204
    assert cli_app._ACTIVE_DRIVERS["dummy_action"].action_executed is True
    cli_app._ACTIVE_DRIVERS.pop("dummy_action", None)


def test_video_route_streams_frame():
    pytest.importorskip("cv2")
    import numpy as np

    app = create_app()
    client = app.test_client()

    dummy_video = DummyRobot()
    dummy_video._latest_frame = np.zeros((2, 2, 3), dtype=np.uint8)
    cli_app._ACTIVE_DRIVERS["dummy_video"] = dummy_video

    res = client.get("/robot/dummy_video/video", stream=True)
    assert res.status_code == 200
    first_chunk = next(res.response)
    assert b"--frame" in first_chunk
    assert b"Content-Type: image/jpeg" in first_chunk
    res.response.close()
    cli_app._ACTIVE_DRIVERS.pop("dummy_video", None)
