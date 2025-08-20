from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import docker
from loguru import logger

from .schemas import ServiceStatusInfo

if TYPE_CHECKING:
    from docker.models.containers import Container


def get_service_status(name_prefix: str = "recurve") -> list[ServiceStatusInfo]:
    client = docker.from_env()
    containers: list[Container] = client.containers.list(all=True)
    result: list[ServiceStatusInfo] = []
    for container in containers:
        if not container.name.startswith(name_prefix):
            continue

        result.append(ServiceStatusInfo(container_name=container.name, status=container.status))

    return result


@cache
def get_docker_root_dir() -> str:
    client = docker.from_env()
    folder = client.info().get("DockerRootDir", "/var/lib/docker")
    if not Path(folder).exists():
        logger.warning(f"docker root dir {folder} does not exist! falling back to /")
        return "/"
    return folder
