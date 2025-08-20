from __future__ import annotations
import socket
import threading
import time
from typing import Dict

from cyberwave_robotics_integrations.base_robot import FlyingDrone
from cyberwave_robotics_integrations.registry import register


@register
class TelloDriver(FlyingDrone):
    """Driver for DJI Tello drone, handling UDP commands and telemetry."""

    def __init__(
        self,
        ip: str = "192.168.10.1",
        command_port: int = 8889,
        state_port: int = 8890,
        video_port: int = 11111,
    ):
        """Initialize driver connection information."""
        super().__init__()
        self.ip = ip
        self.command_port = command_port
        self.state_port = state_port
        self.video_port = video_port
        self.command_sock: socket.socket | None = None
        self.state_sock: socket.socket | None = None
        self.video_sock: socket.socket | None = None
        self._telemetry: Dict[str, str] = {}
        self._running = False

        # Video (raw UDP handler)
        self._video_running = False

        # Video (OpenCV capture handler)
        self._video_capture = None
        self._video_thread: threading.Thread | None = None
        self._latest_frame = None

    def connect(self, *args, **kwargs) -> None:
        """Connect to the Tello drone via UDP and start telemetry streaming."""
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_sock.bind(("", 0))
        self.command_sock.settimeout(5.0)
        try:
            self.command_sock.sendto(b"command", (self.ip, self.command_port))
            data, _ = self.command_sock.recvfrom(1024)
            if data.decode("utf-8").strip().lower() != "ok":
                raise RuntimeError("Failed to enter SDK mode on Tello")
        except socket.timeout:
            raise RuntimeError("No response from Tello on connect()")
        self.connected = True
        self._running = True
        threading.Thread(target=self._listen_telemetry, daemon=True).start()
        print(f"Connected to Tello at {self.ip}")

    def _listen_telemetry(self) -> None:
        """Background thread to receive telemetry from Tello."""
        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.bind(("", self.state_port))
        self.state_sock.settimeout(1.0)
        while self._running:
            try:
                data, _ = self.state_sock.recvfrom(1024)
            except socket.timeout:
                continue
            state_str = data.decode("utf-8").strip()
            tel = {}
            for pair in state_str.split(";"):
                if not pair:
                    continue
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    tel[k] = v
            self._telemetry = tel
        self.state_sock.close()

    # ------------------------------------------------------------------
    # Video Streaming (Raw UDP version, for custom handlers)
    # ------------------------------------------------------------------
    def start_video(self, frame_handler=None) -> None:
        """Begin streaming video frames from the Tello using raw UDP."""
        if not self.connected:
            raise RuntimeError("Tello not connected")
        if self._video_running:
            return
        self.video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_sock.bind(("", self.video_port))
        self.video_sock.settimeout(1.0)
        self.command_sock.sendto(b"streamon", (self.ip, self.command_port))
        self._video_running = True

        def _recv() -> None:
            while self._video_running:
                try:
                    data = self.video_sock.recv(2048)
                except socket.timeout:
                    continue
                if frame_handler:
                    frame_handler(data)

        threading.Thread(target=_recv, daemon=True).start()

    def stop_video(self) -> None:
        """Stop streaming video frames (raw UDP)."""
        if not self._video_running:
            return
        self._video_running = False
        try:
            self.command_sock.sendto(b"streamoff", (self.ip, self.command_port))
        except Exception:
            pass
        if self.video_sock:
            self.video_sock.close()
            self.video_sock = None

    # ------------------------------------------------------------------
    # Video Streaming (OpenCV version)
    # ------------------------------------------------------------------
    def start_video_stream(self, frame_callback=None) -> None:
        """Begin streaming video using OpenCV in a background thread."""
        if not self.connected:
            raise RuntimeError("Tello not connected")

        if self._video_running:
            return

        if self.command_sock is None:
            raise RuntimeError("No command socket available")

        self.command_sock.sendto(b"streamon", (self.ip, self.command_port))

        try:
            import cv2  # type: ignore
        except Exception as exc:
            raise RuntimeError("OpenCV required for video streaming") from exc

        self._video_capture = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)
        if not self._video_capture.isOpened():
            self._video_capture.release()
            self._video_capture = None
            raise RuntimeError("Failed to open Tello video stream")

        self._video_running = True

        def _reader() -> None:
            while self._video_running and self._video_capture is not None:
                ret, frame = self._video_capture.read()
                if not ret:
                    time.sleep(0.01)
                    continue
                self._latest_frame = frame
                if frame_callback:
                    try:
                        frame_callback(frame)
                    except Exception:
                        pass
            if self._video_capture is not None:
                self._video_capture.release()
                self._video_capture = None

        self._video_thread = threading.Thread(target=_reader, daemon=True)
        self._video_thread.start()

    def stop_video_stream(self) -> None:
        """Stop OpenCV-based video stream and clean up resources."""
        if not self._video_running:
            return

        self._video_running = False
        if self.command_sock is not None:
            try:
                self.command_sock.sendto(b"streamoff", (self.ip, self.command_port))
            except Exception:
                pass

        if self._video_thread is not None:
            self._video_thread.join(timeout=1.0)
            self._video_thread = None

    # ------------------------------------------------------------------
    # Drone Control
    # ------------------------------------------------------------------
    def takeoff(self) -> None:
        """Command the Tello drone to take off."""
        if not self.connected:
            raise RuntimeError("Tello not connected")
        self.command_sock.sendto(b"takeoff", (self.ip, self.command_port))
        print("Tello taking off...")

    def land(self) -> None:
        """Command the Tello drone to land."""
        if not self.connected:
            raise RuntimeError("Tello not connected")
        self.command_sock.sendto(b"land", (self.ip, self.command_port))
        self._running = False
        print("Tello landing...")

    def scan_environment(self) -> None:
        """Perform an environment scan (rotate 360 degrees)."""
        if not self.connected:
            raise RuntimeError("Tello not connected")
        self.command_sock.sendto(b"cw 360", (self.ip, self.command_port))
        print("Tello performing a 360-degree scan...")

    def disconnect(self) -> None:
        """Disconnect from the Tello drone and clean up resources."""
        if self.connected:
            try:
                self.command_sock.sendto(b"land", (self.ip, self.command_port))
            except Exception:
                pass
        # Ensure any active video streams are stopped before shutting down
        if self._video_running:
            try:
                self.stop_video_stream()
            except Exception:
                try:
                    self.stop_video()
                except Exception:
                    pass
        self._running = False
        if self.state_sock:
            self.state_sock.close()
        if self.command_sock:
            self.command_sock.close()
        self.connected = False
        print("Disconnected from Tello.")

    def get_status(self) -> Dict[str, str]:
        """Return the latest telemetry data."""
        return dict(self._telemetry)

    @classmethod
    def supports(cls, asset) -> bool:
        rid = ((getattr(asset, "metadata", None) or {}).get("registry_id") or "").lower()
        name = (getattr(asset, "name", "") or "").lower()
        return "tello" in rid or "dji/tello" in rid or "tello" in name
