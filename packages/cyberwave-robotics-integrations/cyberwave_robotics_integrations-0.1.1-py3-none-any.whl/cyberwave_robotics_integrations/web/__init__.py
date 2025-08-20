from __future__ import annotations

from flask import Flask, jsonify, render_template, Response
from cyberwave_robotics_integrations.cli.app import _ACTIVE_DRIVERS
from rich import print
import time

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None  # type: ignore
    print(
        "[yellow]OpenCV not installed – video streaming will be unavailable.[/yellow]"
    )


def create_app() -> Flask:
    """Return configured Flask application for the dashboard."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.route("/")
    def index():
        robots = [
            {"alias": alias, "type": r.__class__.__name__}
            for alias, r in _ACTIVE_DRIVERS.items()
        ]
        return render_template("dashboard.html", robots=robots)

    @app.route("/robot/<alias>/telemetry")
    def telemetry(alias: str):
        robot = _ACTIVE_DRIVERS.get(alias)
        if robot and hasattr(robot, "get_status"):
            return jsonify(robot.get_status())
        return jsonify({})

    @app.route("/robot/<alias>/command/<cmd>", methods=["POST"])
    def command(alias: str, cmd: str):
        robot = _ACTIVE_DRIVERS.get(alias)
        if not robot:
            return "", 404
        try:
            getattr(robot, cmd)()
            return "", 204
        except Exception as exc:  # pragma: no cover - simple error pass through
            return str(exc), 500

    @app.route("/robot/<alias>/video")
    def video(alias: str):
        if cv2 is None:
            return (
                "OpenCV not available. Install 'opencv-python' for video streaming.",
                503,
            )
        robot = _ACTIVE_DRIVERS.get(alias)
        if not (robot and hasattr(robot, "_latest_frame")):
            return "No video", 404

        def gen():
            while True:
                frame = robot._latest_frame
                if frame is not None:
                    ok, buf = cv2.imencode(".jpg", frame)
                    if ok:
                        yield (
                            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
                        )
                time.sleep(0.03)

        return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

    return app
