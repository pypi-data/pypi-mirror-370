import asyncio
import os
import platform
import pwd
import subprocess
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List

import typer

from ..config import RECURVE_HOME
from ..exceptions import PermissionDeniedException
from ..utils import find_recurve_home, find_systemd_service_dir
from ._typer import RecurveTyper, exit_with_error

service_app: typer.Typer = RecurveTyper(name="service", help="Commands for installing as service hosted by systemd.")

SERVICE_CFG_CONTENT: str = """[Unit]
Description=Reorc Agent Service
After=network.target
# always try to start the service
StartLimitIntervalSec=0
StartLimitBurst=0

[Service]
User={os_user}
Group={os_user}
ExecStart={agent_path} agent start
Restart=on-failure
# Restart after exit with 15 seconds
RestartSec=15s
Environment=PYTHONUNBUFFERED=1
StandardOutput=append:{service_log_dir}/agent.log
StandardError=append:{service_log_dir}/agent.log

[Install]
WantedBy=multi-user.target
"""


def linux_only(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to ensure command only runs on Linux systems"""

    @wraps(f)
    async def wrapper(*args, **kwargs):
        if platform.system() != "Linux":
            exit_with_error("This command is only supported on Linux systems")
        return await f(*args, **kwargs)

    return wrapper


async def _try_execute(commands: List[str], use_sudo: bool = False) -> tuple[bytes, bytes]:
    """Try to execute commands with or without sudo"""
    try:
        if use_sudo:
            process = await asyncio.create_subprocess_exec(
                "sudo",
                "sh",
                "-c",
                " && ".join(commands),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        else:
            process = await asyncio.create_subprocess_exec(
                "sh", "-c", " && ".join(commands), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, commands, stderr)
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        if not use_sudo:
            return await _try_execute(commands, use_sudo=True)
        raise e


@service_app.command()
@linux_only
async def install() -> None:
    """Install the systemd service configuration."""
    from .._internal.agent import Agent

    service_name: str = "reorc-agent"
    service_config_path: Path = RECURVE_HOME / f"{service_name}.service"
    service_log_path: Path = Path("/var/log/reorc")
    exec_file_path: Path = Path(os.path.dirname(sys.executable) + "/reorc")
    systemd_path: Path = find_systemd_service_dir()
    symlink_path: Path = systemd_path / f"{service_name}.service"
    os_user_info: pwd.struct_passwd = pwd.getpwnam(find_recurve_home().owner())

    if not systemd_path.exists():
        exit_with_error("Failed to find systemd service directory")

    agent = Agent.default()
    if not agent.has_logged_in:
        exit_with_error("Agent not logged in.")

    try:
        commands = []

        if not service_log_path.exists():
            commands.extend(
                [
                    f"mkdir -p {service_log_path}",
                    f"chown {os_user_info.pw_name}:{os_user_info.pw_name} {service_log_path}",
                ]
            )

        content_to_write = SERVICE_CFG_CONTENT.format(
            os_user=os_user_info.pw_name, agent_path=exec_file_path, service_log_dir=service_log_path
        )

        typer.secho(f"Writing service content to {service_config_path}:", fg="green")
        typer.secho(content_to_write, fg="green")

        with open(service_config_path, "w") as f:
            f.write(content_to_write)

        commands.extend(
            [
                f"ln -sf {service_config_path} {symlink_path}",
                "systemctl daemon-reload",
                f"systemctl start {service_name}",
                f"systemctl enable {service_name}",
            ]
        )

        try:
            await _try_execute(commands)
            typer.secho(f"Successfully installed systemd service to {service_config_path}", fg="green")
            typer.secho(f"Created symlink {symlink_path} -> {service_config_path}", fg="green")
        except subprocess.CalledProcessError as e:
            exit_with_error(f"Error executing commands: {e.stderr.decode()}")

    except PermissionDeniedException:
        exit_with_error("Error: Permission denied, try running with sudo")
    except OSError as e:
        exit_with_error(f"Error: Failed to perform file operations: {e}")
