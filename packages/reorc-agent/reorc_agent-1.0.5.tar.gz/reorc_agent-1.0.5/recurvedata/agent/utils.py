import os
import subprocess
from pathlib import Path
from typing import List

import typer

from .config import RECURVE_HOME
from .exceptions import PathNotFoundException

SYSTEMD_CANDIDATE_PATHS: List[Path] = [
    Path("/etc/systemd/system/"),
    Path("/run/systemd/system/"),
    Path("/usr/lib/systemd/system/"),
    Path("/lib/systemd/system/"),
]


def find_recurve_home() -> Path:
    """find the recurve home ignore if running as root"""
    # root user
    if os.geteuid() == 0:
        if RECURVE_HOME.exists():
            typer.secho(f"Found RECURVE_HOME with const as root: {RECURVE_HOME}", fg="green")
            return RECURVE_HOME

        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            # find env
            result = subprocess.check_output(
                ["su", "-", sudo_user, "-c", "echo $RECURVE_HOME"], universal_newlines=True
            )
            if result:
                typer.secho(f"Found RECURVE_HOME in env variables: {result.strip()}", fg="green")
                return Path(result.strip())
            else:
                default_path = Path("/home/" + sudo_user + "/.recurve")
                if default_path.exists():
                    typer.secho(f"Found RECURVE_HOME in default path: {default_path}", fg="green")
                    return default_path
    # non-root user
    else:
        if RECURVE_HOME.exists():
            typer.secho(f"Found RECURVE_HOME with const: {RECURVE_HOME}", fg="green")
            return RECURVE_HOME
    raise PathNotFoundException("Path RECURVE_HOME not found")


def find_systemd_service_dir() -> Path:
    """Find systemd service directory synchronously"""
    for path in SYSTEMD_CANDIDATE_PATHS:
        if path.exists():
            return path

    try:
        result = subprocess.check_output(["whereis", "systemd"], universal_newlines=True)
        if ":" in result:
            path_strs = result.split(":")[1].split()
            for path_str in path_strs:
                path = Path(path_str.rstrip("/") + "/system/")
                if path.exists() and path.is_dir():
                    return path
    except (subprocess.CalledProcessError, IndexError) as e:
        raise PathNotFoundException(f"No systemd service directory found, caused by: {str(e)}")

    raise PathNotFoundException("No systemd service directory found")
