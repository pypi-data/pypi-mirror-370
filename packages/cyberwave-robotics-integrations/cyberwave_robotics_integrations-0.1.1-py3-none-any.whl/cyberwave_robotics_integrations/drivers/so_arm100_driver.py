"""Driver for the physical SO-ARM100 robotic arm."""
from __future__ import annotations
import logging
from typing import Optional

from cyberwave_robotics_integrations.base_robot import ArmRobot

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover - serial may not be available during tests
    serial = None  # type: ignore

logger = logging.getLogger(__name__)


class SoArm100Driver(ArmRobot):
    """Driver that communicates with the SO-ARM100 via a serial connection."""

    form_factor = "arm"
    JOINT_LIMITS = [(-180.0, 180.0) for _ in range(6)]

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, *args, **kwargs) -> None:
        super().__init__(*args, joint_limits=self.JOINT_LIMITS, **kwargs)
        self.port = port
        self.baudrate = baudrate
        self._serial: Optional[serial.Serial] = None  # type: ignore[name-defined]
        self._predefined_actions.update({"home": [0.0 for _ in range(6)]})

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    def connect(self, *args, **kwargs) -> None:
        if serial is None:
            raise RuntimeError("pyserial package required for SO-ARM100 driver")
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as exc:  # pragma: no cover - hardware specific
            raise RuntimeError(f"Failed to open serial port {self.port}") from exc
        self.connected = True
        logger.info("Connected to SO-ARM100 on %s", self.port)

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:  # pragma: no cover - hardware specific
                pass
            self._serial = None
        self.connected = False
        logger.info("Disconnected from SO-ARM100")

    # ------------------------------------------------------------------
    # Low level helpers
    # ------------------------------------------------------------------
    def _send(self, command: str) -> None:
        if self._serial is None:
            raise RuntimeError("Robot not connected")
        data = command.strip() + "\n"
        self._serial.write(data.encode("ascii"))

    def _readline(self) -> str:
        if self._serial is None:
            raise RuntimeError("Robot not connected")
        line = self._serial.readline().decode("ascii", errors="ignore").strip()
        return line

    # ------------------------------------------------------------------
    # ArmRobot overrides
    # ------------------------------------------------------------------
    def set_joint_positions(self, pos_list):
        super().set_joint_positions(pos_list)
        if self._serial is not None:
            angles = " ".join(str(a) for a in self._joints)
            self._send(f"SET {angles}")

    def move_to(self, pose) -> None:
        """Move the arm to a named pose or coordinate."""
        if self._serial is None:
            raise RuntimeError("Robot not connected")
        self._send(f"MOVE {pose}")

    def grip(self, open: bool) -> None:
        """Open or close the gripper."""
        if self._serial is None:
            raise RuntimeError("Robot not connected")
        cmd = "GRIP OPEN" if open else "GRIP CLOSE"
        self._send(cmd)

    def get_joint_positions(self):
        if self._serial is not None:
            try:
                self._send("GET")
                line = self._readline()
                parts = [float(p) for p in line.split()]
                if len(parts) == len(self._joints):
                    self._joints = parts
            except Exception:  # pragma: no cover - hardware specific
                logger.debug("Failed to read joint positions", exc_info=True)
        return super().get_joint_positions()
