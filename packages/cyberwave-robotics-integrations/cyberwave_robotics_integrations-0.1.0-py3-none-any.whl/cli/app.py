"""CLI plugin for managing robot drivers."""

import json
import time
import asyncio
import threading
from pathlib import Path
import webbrowser

import typer
from rich import print

from cyberwave_robotics_integrations.factory import Robot
from cyberwave_robotics_integrations.base_robot import BaseRobot
from cyberwave import Client

# Dictionary of all active drivers mapped by alias
_ACTIVE_DRIVERS: dict[str, BaseRobot] = {}

app = typer.Typer(help="Manage robot drivers")

# ~/.cyberwave holds per-user config and the latest cached telemetry
_CONFIG_DIR = Path.home() / ".cyberwave"


# --------------------------------------------------------------------------- #
#  Simple sub-commands                                                        #
# --------------------------------------------------------------------------- #
@app.command()
def install(driver_name: str) -> None:
    """Install a driver. For bundled drivers this is a no-op."""
    print(f"[green]Driver '{driver_name}' is ready for use.[/green]")


@app.command()
def configure(
    driver_name: str,
    ip: str = typer.Argument(..., help="Drone IP address"),
) -> None:
    """Configure driver connection settings."""
    if driver_name == "tello":
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        alias = driver_name  # default alias for configure
        cfg = _CONFIG_DIR / f"tello_config_{alias}.json"
        tmp = cfg.with_suffix(".tmp")
        tmp.write_text(json.dumps({"ip": ip}))
        tmp.replace(cfg)
        print(f"[green]Configured Tello IP as {ip}[/green]")
    else:
        print(f"[yellow]No configuration needed for driver '{driver_name}'[/yellow]")


# --------------------------------------------------------------------------- #
#  start                                                                      #
# --------------------------------------------------------------------------- #
@app.command()
def start(
    driver_name: str,
    alias: str = typer.Option(None, "--alias", help="Unique name for this robot instance"),
    token: str = typer.Option("", "--token", help="Offline token"),
    device_id: int = typer.Option(
        None,
        "--device-id",
        help="Device ID to which live telemetry should be uploaded",
    ),
    video: bool = typer.Option(
        False,
        "--video/--no-video",
        help="Enable video streaming while the driver runs",
    ),
    persistent: bool = typer.Option(
        True,
        "--persistent/--no-persistent",
        help="Keep process alive until interrupted",
    ),
) -> None:
    """Start a driver service and connect to the robot."""

    # Determine alias and ensure uniqueness
    if alias is None:
        alias = driver_name
    original_alias = alias
    idx = 2
    while alias in _ACTIVE_DRIVERS:
        alias = f"{original_alias}-{idx}"
        idx += 1

    connection_kwargs = {}
    # Resolve optional IP for Tello
    tello_cfg = None
    if driver_name == "tello":
        ip = "192.168.10.1"
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        tello_cfg = _CONFIG_DIR / f"tello_config_{alias}.json"
        cfg_to_read = tello_cfg
        legacy_cfg = _CONFIG_DIR / "tello_config.json"
        if not cfg_to_read.exists() and legacy_cfg.exists():
            cfg_to_read = legacy_cfg
        if cfg_to_read.exists():
            try:
                ip = json.loads(cfg_to_read.read_text()).get("ip", ip)
            except json.JSONDecodeError:
                pass
        connection_kwargs["ip"] = ip
        print(f"Connecting to Tello at {ip} …")
    else:
        print(f"Connecting to {driver_name} …")

    try:
        robot = Robot(driver_name, **connection_kwargs)
        robot.connect()
    except Exception as exc:
        print(f"[red]Failed to start {driver_name} driver: {exc}[/red]")
        raise typer.Exit(code=1)

    # ---------------------------------------------------------------------------- #
    #  Merge result: combine state tracking *and* cloud-telemetry upload            #
    # ---------------------------------------------------------------------------- #
    _ACTIVE_DRIVERS[alias] = robot

    client: Client | None = None
    project_id: int | None = None
    if device_id is None:
        try:
            from cyberwave_cli import config as cli_config
            project_id = getattr(cli_config, "DEFAULT_PROJECT", None)
        except Exception:
            project_id = None
        if project_id is not None:
            client = Client(use_token_cache=False)
            if token:
                client._access_token = token
            try:
                info = asyncio.run(
                    client.register_device(
                        project_id=project_id,
                        name=alias,
                        device_type=driver_name,
                    )
                )
                device_id = info.get("id")
                print(f"Registered new device with ID {device_id}")
                try:
                    webbrowser.open(
                        f"https://.../projects/{project_id}/devices/{device_id}"
                    )
                except Exception:
                    pass
            except Exception as exc:
                print(f"[yellow]Failed to auto-register device: {exc}[/yellow]")
    if device_id is not None and client is None:
        client = Client(use_token_cache=False)
        if token:
            client._access_token = token

    if video:
        def _frame_handler(frame: bytes) -> None:
            if client is not None:
                try:
                    asyncio.run(
                        client.upload_video_frame(
                            device_id=device_id, frame_bytes=frame
                        )
                    )
                except Exception:
                    pass

        try:
            if hasattr(robot, "start_video_stream"):
                robot.start_video_stream(_frame_handler)
            elif hasattr(robot, "start_video"):
                try:
                    robot.start_video(_frame_handler)
                except TypeError:
                    robot.start_video()
            else:
                print(
                    "[yellow]Video streaming not supported by this driver.[/yellow]"
                )
        except Exception as exc:
            print(f"[yellow]Warning: Video stream could not start: {exc}[/yellow]")
            if "OpenCV" in str(exc):
                print(
                    "[yellow]Install the 'opencv-python' package to enable video streaming.[/yellow]"
                )

    # Cache initial telemetry
    telemetry = {}
    if hasattr(robot, "get_status"):
        try:
            telemetry = robot.get_status() or {}
        except Exception:
            telemetry = {}
    if driver_name == "tello" and tello_cfg is not None:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        tmp = tello_cfg.with_suffix(".tmp")
        tmp.write_text(json.dumps({"ip": connection_kwargs.get("ip", ""), "telemetry": telemetry}))
        tmp.replace(tello_cfg)

    def _telemetry_loop(alias: str, robot: BaseRobot, client: Client | None, device_id: int | None) -> None:
        while _ACTIVE_DRIVERS.get(alias) is robot:
            data = {}
            if hasattr(robot, "get_status"):
                try:
                    data = robot.get_status() or {}
                except Exception:
                    data = {}
            if driver_name == "tello" and tello_cfg is not None:
                _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                tmp = tello_cfg.with_suffix(".tmp")
                tmp.write_text(json.dumps({"ip": connection_kwargs.get("ip", ""), "telemetry": data}))
                tmp.replace(tello_cfg)
            if client is not None:
                try:
                    asyncio.run(client.send_telemetry(device_id=device_id, telemetry=data))
                except Exception:
                    pass
            time.sleep(1)

    threading.Thread(
        target=_telemetry_loop,
        args=(alias, robot, client, device_id),
        daemon=False,
    ).start()

    print(f"[green]{driver_name.capitalize()} driver '{alias}' started successfully.[/green]")

    if persistent:
        print("[green]Driver started. Press Ctrl+C to stop.[/green]")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("[yellow]Shutting down driver...[/yellow]")
            stop(alias=alias, video=video)


# --------------------------------------------------------------------------- #
#  stop                                                                       #
# --------------------------------------------------------------------------- #
@app.command()
def stop(
    alias: str = typer.Argument(..., help="Name or alias of the robot to stop"),
    video: bool = typer.Option(False, "--video", help="Stop video streaming"),
) -> None:
    """Stop a driver service and disconnect from the robot."""

    robot = _ACTIVE_DRIVERS.get(alias)
    if robot is None:
        matching = [
            name
            for name, r in _ACTIVE_DRIVERS.items()
            if r.__class__.__name__.lower().startswith(alias.lower())
        ]
        if len(matching) > 1:
            print(
                f"[yellow]Multiple robots match '{alias}': {', '.join(matching)}. "
                "Please specify the full alias.[/yellow]"
            )
            return
        if len(matching) == 1:
            alias = matching[0]
            robot = _ACTIVE_DRIVERS.get(alias)

    if robot is None:
        print(f"[yellow]No running robot with name '{alias}'.[/yellow]")
        return

    if video:
        if hasattr(robot, "stop_video_stream"):
            try:
                robot.stop_video_stream()
            except Exception as exc:
                print(f"[yellow]Failed to stop video: {exc}[/yellow]")
        elif hasattr(robot, "stop_video"):
            try:
                robot.stop_video()
            except Exception as exc:
                print(f"[yellow]Failed to stop video: {exc}[/yellow]")

    try:
        robot.disconnect()
    except Exception as exc:
        print(f"[yellow]Error while disconnecting: {exc}[/yellow]")

    _ACTIVE_DRIVERS.pop(alias, None)
    print(f"[green]Stopped robot '{alias}'.[/green]")


# --------------------------------------------------------------------------- #
#  status                                                                     #
# --------------------------------------------------------------------------- #
@app.command()
def status(alias: str = typer.Argument(None, help="Robot alias or driver name to query (omit to show all)")) -> None:
    """Show status for active robot drivers."""
    if alias is None:
        if not _ACTIVE_DRIVERS:
            print("[yellow]No drivers are currently running.[/yellow]")
        for name, robot in _ACTIVE_DRIVERS.items():
            tel = robot.get_status() if hasattr(robot, "get_status") else {}
            print(f"{name}: {tel if tel else 'No telemetry available'}")
    else:
        robot = _ACTIVE_DRIVERS.get(alias)
        if robot:
            tel = robot.get_status() if hasattr(robot, "get_status") else {}
            print(f"{alias}: {tel if tel else 'No telemetry available'}")
            return
        matching = [(name, r) for name, r in _ACTIVE_DRIVERS.items() if r.__class__.__name__.lower().startswith(alias.lower())]
        if not matching:
            print(f"[yellow]No active drivers match '{alias}'.[/yellow]")
        elif len(matching) == 1:
            name, robot = matching[0]
            tel = robot.get_status() if hasattr(robot, "get_status") else {}
            print(f"{name} ({alias}): {tel if tel else 'No telemetry available'}")
        else:
            print(f"[green]Multiple '{alias}' drivers active:[/green]")
            for name, robot in matching:
                tel = robot.get_status() if hasattr(robot, "get_status") else {}
            print(f"  {name}: {tel if tel else 'No telemetry'}")


# --------------------------------------------------------------------------- #
#  cmd                                                                       #
# --------------------------------------------------------------------------- #
@app.command()
def cmd(
    alias: str = typer.Argument(..., help="Alias of the running robot"),
    method: str = typer.Argument(..., help="Driver method name to call"),
) -> None:
    """Invoke a method on a running robot driver."""

    robot = _ACTIVE_DRIVERS.get(alias)
    if robot is None:
        matches = [name for name in _ACTIVE_DRIVERS if name.lower().startswith(alias.lower())]
        if len(matches) == 1:
            alias = matches[0]
            robot = _ACTIVE_DRIVERS[alias]
        else:
            if len(matches) > 1:
                print(f"[yellow]Multiple robots match '{alias}'. Please use a unique alias.[/yellow]")
            else:
                print(f"[yellow]No running robot with alias '{alias}'.[/yellow]")
            raise typer.Exit(code=1)

    if not hasattr(robot, method):
        print(f"[red]Driver '{alias}' has no method '{method}'.[/red]")
        raise typer.Exit(code=1)

    func = getattr(robot, method)
    if not callable(func):
        print(f"[red]Attribute '{method}' on '{alias}' is not callable.[/red]")
        raise typer.Exit(code=1)

    try:
        result = func()
    except Exception as exc:
        print(f"[red]Error while invoking {method} on '{alias}': {exc}[/red]")
        raise typer.Exit(code=1)

    if result is not None:
        print(result)

    print(f"[green]Successfully called {method}() on '{alias}'.[/green]")


# --------------------------------------------------------------------------- #
#  record-video                                                               #
# --------------------------------------------------------------------------- #
@app.command(name="record-video")
def record_video(
    driver_name: str,
    output: Path = typer.Option("tello_video.bin", "--output", help="File to save raw frames"),
    duration: int = typer.Option(5, "--duration", help="Recording duration in seconds"),
) -> None:
    """Record a short video clip from the robot."""
    if driver_name != "tello":
        print(f"[red]Video recording for driver '{driver_name}' not implemented.[/red]")
        return

    robot = Robot("tello")
    robot.connect()
    frames: list[bytes] = []
    robot.start_video(lambda f: frames.append(f))
    time.sleep(duration)
    robot.stop_video()
    robot.disconnect()
    with output.open("wb") as fh:
        for frame in frames:
            fh.write(frame)
    print(f"[green]Saved {len(frames)} frames to {output}[/green]")


# --------------------------------------------------------------------------- #
#  serve                                                                      #
# --------------------------------------------------------------------------- #
@app.command()
def serve(
    drivers: list[str] = typer.Option([], "--driver", help="Start given drivers"),
    host: str = "127.0.0.1",
    port: int = 5000,
) -> None:
    """Launch a simple web dashboard and optionally start drivers."""

    for entry in drivers:
        parts = entry.split(":")
        driver = parts[0]
        alias = parts[1] if len(parts) > 1 else None
        start.callback(driver, alias=alias or driver, video=True, persistent=False)

    from cyberwave_robotics_integrations.web import create_app

    app_ = create_app()
    try:
        app_.run(host=host, port=port)
    finally:
        for a, r in list(_ACTIVE_DRIVERS.items()):
            try:
                if hasattr(r, "stop_video_stream"):
                    r.stop_video_stream()
            except Exception:
                pass
            try:
                r.disconnect()
            except Exception:
                pass
            _ACTIVE_DRIVERS.pop(a, None)
