import asyncio
import os
from collections.abc import Sequence
from copy import deepcopy
import shutil
from typing import Callable, TypeAlias

import aiofiles
from docker.models.containers import Container
from docker.models.images import Image
from loguru import logger

from recurvedata.agent._internal.client import AgentClient
from recurvedata.agent._internal.cube.push_config import cube_push_config_service
from recurvedata.agent._internal.cube.restart_service import cube_restart_service
from recurvedata.agent._internal.docker import docker_client
from recurvedata.agent.config import CONFIG, RECURVE_HOME

from .schemas import (
    Action,
    ContainerManagementPayload,
    CubePushConfigPayload,
    CubeRestartServicePayload,
    DeployServicePayload,
    DeployServiceResult,
    UndeployServicePayload,
    WorkerManagementPayload,
)

COMPOSE_FILE_NAME = os.path.join(RECURVE_HOME, "docker-compose.yml")
COMPOSE_PROJECT_NAME = "recurve_services"
CUBE_DIR = os.path.join(RECURVE_HOME, "cube")
CUBE_CONF_DIR = os.path.join(CUBE_DIR, "conf")
DEFAULT_DOCKER_COMPOSE_CMD = ["docker", "compose", "-f", COMPOSE_FILE_NAME, "-p", COMPOSE_PROJECT_NAME, "up", "-d"]

# Type aliases
TaskList: TypeAlias = Sequence[asyncio.Task[None]]


registry: dict[Action, Callable[[], None]] = {}


def register_action(action_type: Action):
    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        registry[action_type] = func
        return func

    return decorator


def get_run_env() -> dict[str, str]:
    env = os.environ.copy()
    env["RECURVE_HOME"] = str(RECURVE_HOME)
    return env


class WorkerManagementTask:
    @staticmethod
    async def _create_cube_conf_dir(payload: DeployServicePayload) -> None:
        if not payload.cube_env:
            return

        if not os.path.exists(CUBE_CONF_DIR):
            os.makedirs(CUBE_CONF_DIR)

        if payload.cube_env:
            async with aiofiles.open(os.path.join(CUBE_CONF_DIR, ".env"), "w") as f:
                await f.write(payload.cube_env)

        if payload.cube_python:
            # async with aiofiles.open(os.path.join(CUBE_CONF_DIR, "cube.py"), "w") as f:
            # await f.write(payload.cube_python)
            client = AgentClient(CONFIG)
            response = await client.request("GET", "/api/cube/config/cube-python")
            if response.get("cube_python"):
                cube_python_file = response.get("cube_python")
            else:
                cube_python_file = payload.cube_python

            async with aiofiles.open(os.path.join(CUBE_CONF_DIR, "cube.py"), "w") as f:
                await f.write(cube_python_file)

    @staticmethod
    async def _write_cube_proxy_config(payload: DeployServicePayload) -> None:
        if not payload.cube_proxy_config:
            return

        tasks: list[asyncio.Task[None]] = []
        proxy_config = payload.cube_proxy_config
        if proxy_config and isinstance(proxy_config, dict):
            for key, value in proxy_config.items():
                tasks.append(asyncio.create_task(WorkerManagementTask._write_proxy_config_file(str(key), str(value))))
            await asyncio.gather(*tasks)

    @staticmethod
    async def _write_proxy_config_file(key: str, value: str) -> None:
        file_path = os.path.join(CUBE_DIR, f"{key}.toml")

        # Remove if it's a directory
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)

        async with aiofiles.open(file_path, "w") as f:
            await f.write(value)

    @staticmethod
    async def _write_docker_compose_file(payload: DeployServicePayload) -> None:
        async with aiofiles.open(COMPOSE_FILE_NAME, "w") as f:
            await f.write(payload.docker_compose)

    @staticmethod
    async def _fetch_local_image_version(worker_image: str) -> str:
        try:
            image: Image = await asyncio.to_thread(docker_client.images.get, worker_image)
            worker_version = image.labels.get("VERSION")
            return worker_version or "Unknown version"
        except Exception:
            return f"Image {worker_image} not found."

    @staticmethod
    async def _push_cube_config_task(payload: DeployServicePayload) -> None:
        """Task to push cube config with project_id = None during service deployment."""
        try:
            cube_payload = CubePushConfigPayload(
                action=Action.CUBE_PUSH_CONFIG,
                env_id=payload.env_id,
            )
            # Call the push_cube_config method
            await cube_push_config_service.push_cube_config(cube_payload)
            logger.info(f"Successfully pushed cube config during deployment for env_id: {payload.env_id}")
        except Exception as e:
            logger.error(f"Failed to push cube config during deployment: {e}")

    @staticmethod
    @register_action(Action.DEPLOY)
    async def deploy_service(payload: DeployServicePayload) -> DeployServiceResult | None:
        tasks: list[asyncio.Task[None]] = [
            asyncio.create_task(WorkerManagementTask._create_cube_conf_dir(payload)),
            asyncio.create_task(WorkerManagementTask._write_cube_proxy_config(payload)),
            asyncio.create_task(WorkerManagementTask._write_docker_compose_file(payload)),
            asyncio.create_task(WorkerManagementTask._push_cube_config_task(payload)),
        ]
        await asyncio.gather(*tasks)

        env = get_run_env()

        try:
            process = await asyncio.create_subprocess_exec(
                *DEFAULT_DOCKER_COMPOSE_CMD,
                env=env,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = f"Docker compose failed: {stderr.decode() if stderr else 'Unknown error'}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Docker compose failed: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Docker Compose started successfully.")

        worker_version = await WorkerManagementTask._fetch_local_image_version(payload.worker_image)
        return DeployServiceResult(worker_version=worker_version)

    @staticmethod
    @register_action(Action.UNDEPLOY)
    async def undeploy_service(payload: UndeployServicePayload) -> None:
        try:
            cmd = ["docker", "compose", "-f", COMPOSE_FILE_NAME, "-p", COMPOSE_PROJECT_NAME, "down"]
            if payload.remove_volumes:
                cmd.append("-v")

            env = get_run_env()

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = f"Docker compose failed: {stderr.decode() if stderr else 'Unknown error'}"
                logger.error(error_msg)
                # raise for retry
                raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"Docker compose failed: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Undeploy service successfully")

    @staticmethod
    @register_action(Action.START)
    async def start_container(payload: ContainerManagementPayload) -> None:
        for container_name in payload.container_names:
            try:
                container: Container = await asyncio.to_thread(docker_client.containers.get, container_name)
                await asyncio.to_thread(container.start)
                logger.info(f"Container {container_name} started successfully")
            except Exception as e:
                error_msg = f"Failed to start container {container_name}: {str(e)}"
                logger.error(error_msg)
                raise

    @staticmethod
    @register_action(Action.RESTART)
    async def restart_container(payload: ContainerManagementPayload) -> None:
        for container_name in payload.container_names:
            try:
                container: Container = await asyncio.to_thread(docker_client.containers.get, container_name)
                await asyncio.to_thread(container.restart)
                logger.info(f"Container {container_name} restarted successfully")
            except Exception as e:
                error_msg = f"Failed to restart container {container_name}: {str(e)}"
                logger.error(error_msg)
                raise

    @staticmethod
    @register_action(Action.STOP)
    async def stop_container(payload: ContainerManagementPayload) -> None:
        for container_name in payload.container_names:
            try:
                container: Container = await asyncio.to_thread(docker_client.containers.get, container_name)
                await asyncio.to_thread(container.stop)
                logger.info(f"Container {container_name} stopped successfully")
            except Exception as e:
                error_msg = f"Failed to stop container {container_name}: {str(e)}"
                logger.error(error_msg)
                raise

    @staticmethod
    @register_action(Action.CUBE_PUSH_CONFIG)
    async def push_cube_config(payload: CubePushConfigPayload) -> None:
        await cube_push_config_service.push_cube_config(payload)

    @staticmethod
    @register_action(Action.CUBE_RESTART_SERVICE)
    async def restart_cube_service(payload: CubeRestartServicePayload) -> None:
        await cube_restart_service.restart_cube_service(payload)

    @staticmethod
    @register_action(Action.UPGRADE)
    async def upgrade_service(payload: DeployServicePayload) -> DeployServiceResult | None:
        await asyncio.create_task(WorkerManagementTask._write_docker_compose_file(payload))
        try:
            docker_compose_cmd = deepcopy(DEFAULT_DOCKER_COMPOSE_CMD)
            docker_compose_cmd.append("--force-recreate")
            process = await asyncio.create_subprocess_exec(
                *docker_compose_cmd,
                env=get_run_env(),
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()
            if process.returncode != 0:
                error_msg = f"Upgrade service failed: {stderr.decode() if stderr else 'Unknown error'}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Upgrade service failed: {str(e)}"
            logger.error(error_msg)
            raise

        logger.info("Upgrade service successfully")
        worker_version = await WorkerManagementTask._fetch_local_image_version(payload.worker_image)
        return DeployServiceResult(worker_version=worker_version)

    @staticmethod
    async def handle(payload: WorkerManagementPayload) -> DeployServiceResult | None:
        return await registry[payload.action](payload.payload)
