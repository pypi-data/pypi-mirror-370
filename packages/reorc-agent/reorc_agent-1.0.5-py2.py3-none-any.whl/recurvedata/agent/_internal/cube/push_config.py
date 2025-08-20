import asyncio
import hashlib
import json
import os
import shutil
import tarfile
from pathlib import Path

import aiofiles
import httpx
from loguru import logger

from recurvedata.agent._internal.client import AgentClient
from recurvedata.agent._internal.docker import get_container_port, get_containers_batch
from recurvedata.agent._internal.schemas import CubePushConfigPayload
from recurvedata.agent.config import CONFIG, RECURVE_HOME

# Configuration constants
CUBE_CONTAINER_SUFFIX = "_cube_api_1"
VALIDATION_ENDPOINT = "/api/cube/config/validate-sql-connection"
CACERT_URL = "https://curl.se/ca/cacert.pem"
DEFAULT_CUBE_PORT = "15433"


class CubePushConfigService:
    """Service class for handling cube push configuration operations"""

    def __init__(self):
        self.client = AgentClient(CONFIG)
        self.cube_dir = os.path.join(RECURVE_HOME, "cube")
        self.cube_conf_dir = os.path.join(self.cube_dir, "conf")
        self.cube_connections_dir = os.path.join(self.cube_conf_dir, "connections")
        self.cube_projects_dir = os.path.join(self.cube_conf_dir, "projects")
        self.log_prefix = "[cube-push-config]"

    async def _ensure_cube_conf_dir(self):
        """Ensure cube configuration directory exists asynchronously"""
        await asyncio.to_thread(os.makedirs, self.cube_conf_dir, exist_ok=True)

    async def read_cube_conf_file(self, file_path: str) -> str:
        """Read cube configuration file content asynchronously"""
        async with aiofiles.open(os.path.join(self.cube_conf_dir, file_path), "r") as f:
            return await f.read()

    def filter_containers_to_restart(self, container_names: list[str], restart_cube_api_only: bool) -> list[str]:
        """Filter containers that need to be restarted based on criteria"""
        if not container_names:
            return []

        if restart_cube_api_only:
            return [name for name in container_names if name.endswith(CUBE_CONTAINER_SUFFIX)]

        return container_names

    async def restart_single_container(self, container_name: str, container) -> bool:
        """Restart a single container and return success status"""
        try:
            logger.info(f"{self.log_prefix} prepare restart container: {container_name}")
            await asyncio.to_thread(container.restart)
            logger.info(f"{self.log_prefix} successful restarted container: {container_name}")
            return True
        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to restart container {container_name}: {e}")
            return False

    async def restart_containers_with_lock(self, payload: CubePushConfigPayload, restart_cube_api_only: bool = False):
        """
        Restart containers asynchronously
        Restart containers with Redis lock coordination to prevent concurrent restarts.
        Uses Redis-based cube restarting lock to coordinate across multiple processes.
        """
        if not payload.container_names:
            return

        # Check if another process is already restarting containers
        is_locked = await self.check_cube_lock(lock_type="restarting")
        if is_locked:
            logger.info(f"{self.log_prefix} Another process is already restarting containers, skipping restart")
            return

        # Acquire lock to prevent other processes from concurrent restarts
        # Use TTL of 20 seconds to allow time for container restarts
        if not await self.acquire_cube_lock(ttl=20, lock_type="restarting"):
            logger.warning(f"{self.log_prefix} Failed to acquire restarting lock for container restart, skipping")
            return

        # Filter containers that need to be restarted
        containers_to_restart = self.filter_containers_to_restart(payload.container_names, restart_cube_api_only)

        if not containers_to_restart:
            logger.info(f"{self.log_prefix} No containers to restart")
            return

        # Get containers in batch
        containers = await get_containers_batch(containers_to_restart)

        restarted_containers = []
        failed_containers = []

        for container_name in containers_to_restart:
            if container_name not in containers:
                logger.error(f"{self.log_prefix} Container not found: {container_name}")
                failed_containers.append(container_name)
                continue

            success = await self.restart_single_container(container_name, containers[container_name])
            if success:
                restarted_containers.append(container_name)
            else:
                failed_containers.append(container_name)

        # Log summary
        if restarted_containers:
            logger.info(
                f"{self.log_prefix} Successfully restarted {len(restarted_containers)} containers: {restarted_containers}"
            )

        if failed_containers:
            logger.error(
                f"{self.log_prefix} Failed to restart {len(failed_containers)} containers: {failed_containers}"
            )

    async def download_cacert_pem(self):
        """Download cacert.pem file asynchronously"""
        logger.info(f"{self.log_prefix} Downloading cacert.pem")
        file_name = os.path.join(self.cube_conf_dir, "cacert.pem")

        if await asyncio.to_thread(os.path.exists, file_name):
            logger.info(f"{self.log_prefix} cacert.pem already exists, skip download")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(CACERT_URL)
                response.raise_for_status()

                # Save the content to a file asynchronously
                await self._ensure_cube_conf_dir()
                async with aiofiles.open(file_name, "wb") as f:
                    await f.write(response.content)

            logger.info(f"{self.log_prefix} cacert.pem downloaded successfully.")
        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to download cacert.pem: {e}")
            raise e

    async def fetch_cube_connections(self, payload: CubePushConfigPayload = None) -> int:
        """Fetch cube connections asynchronously"""
        logger.info(f"{self.log_prefix} Fetching cube connections")
        datasources = []
        datasources_counter = 0

        if await asyncio.to_thread(os.path.exists, self.cube_connections_dir):
            conn_files = await asyncio.to_thread(os.listdir, self.cube_connections_dir)
            for conn_file in conn_files:
                datasources.append(conn_file.split(".")[0])

        conn_map = await self.client.request(
            "GET", "/api/cube/config/connections", params={"datasources": ",".join(datasources)}, retries=4
        )

        for datasource, conn in conn_map.items():
            async with aiofiles.open(os.path.join(self.cube_connections_dir, f"{datasource}.json"), "w") as f:
                await f.write(json.dumps(conn, indent=4))
                datasources_counter += 1

        logger.info(f"{self.log_prefix} Cube connections: ({datasources_counter}) fetched successfully")
        return datasources_counter

    async def fetch_updated_env_file(self, payload: CubePushConfigPayload, existing_env_file: str) -> dict:
        """
        Fetch updated env file from server-side API that handles ClickHouse connections
        Returns dict with env_content and change flags
        """
        logger.info(f"{self.log_prefix} Fetching updated env file from server API for project {payload.project_id}")

        if not existing_env_file:
            # Get current env file content after fetch cube config for the first time
            current_env_content = await self.read_cube_conf_file(".env")
        else:
            current_env_content = existing_env_file

        # Get datasources string
        datasources = []
        if await asyncio.to_thread(os.path.exists, self.cube_connections_dir):
            conn_files = await asyncio.to_thread(os.listdir, self.cube_connections_dir)
            for conn_file in conn_files:
                datasources.append(conn_file.split(".")[0])

        # Call server API to get updated env file
        try:
            response = await self.client.request(
                "POST",
                "/api/cube/config/cube-env",
                json={
                    "agent_env_file": current_env_content,
                    "datasources": ",".join(datasources),
                    "project_id": payload.project_id,
                },
                retries=4,
            )

            env_content = response.get("env_content", "")
            has_clickhouse_changes = response.get("has_clickhouse_changes", False)
            has_general_env_changes = response.get("has_general_env_changes", False)

            if env_content:
                logger.info(f"{self.log_prefix} Successfully received updated env file from server")
                logger.info(
                    f"{self.log_prefix} Changes detected - ClickHouse: {has_clickhouse_changes}, General: {has_general_env_changes}"
                )

                # Write the updated env file
                async with aiofiles.open(os.path.join(self.cube_conf_dir, ".env"), "w") as f:
                    await f.write(env_content)

                return {
                    "env_content": env_content,
                    "has_clickhouse_changes": has_clickhouse_changes,
                    "has_general_env_changes": has_general_env_changes,
                }
            else:
                logger.warning(f"{self.log_prefix} Server returned empty env content")
                return {
                    "env_content": current_env_content,
                    "has_clickhouse_changes": False,
                    "has_general_env_changes": False,
                }

        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to fetch updated env file from server: {e}")
            return {
                "env_content": current_env_content,
                "has_clickhouse_changes": False,
                "has_general_env_changes": False,
            }

    async def calculate_md5(self, filepath: Path | str) -> str:
        """Calculate MD5 hash of a file asynchronously"""
        if not os.path.exists(filepath):
            return ""

        md5_hash = hashlib.md5()
        chunk_size = 1024 * 1024

        async with aiofiles.open(filepath, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)

        return md5_hash.hexdigest()

    async def tar_gzip_uncompress(self, tar_gz_path, extract_path):
        """Extract tar.gz file to specified path asynchronously"""
        logger.info(f"{self.log_prefix} extract tar.gz {tar_gz_path} to {extract_path}")
        os.makedirs(extract_path, exist_ok=True)
        await asyncio.to_thread(tarfile.open(tar_gz_path, "r:gz").extractall, path=extract_path)

    def remove_non_empty_dir(self, path):
        """Remove directory and all its contents using shutil.rmtree for robustness"""
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                logger.info(f"{self.log_prefix} Successfully removed directory: {path}")
            except Exception as e:
                logger.error(f"{self.log_prefix} Failed to remove directory {path}: {e}")
                # Try alternative approach if shutil.rmtree fails
                try:
                    # Force removal with ignore_errors=True as fallback
                    shutil.rmtree(path, ignore_errors=True)
                    logger.info(f"{self.log_prefix} Forcefully removed directory: {path}")
                except Exception as e2:
                    logger.error(f"{self.log_prefix} Failed to forcefully remove directory {path}: {e2}")
                    raise e

    def build_request_params(self, payload: CubePushConfigPayload) -> dict:
        """Build request parameters from payload"""
        params = {}
        if payload.project_id:
            params["project_id"] = payload.project_id

        if payload.cube_ids:
            params["cube_ids"] = ",".join(str(cube_id) for cube_id in payload.cube_ids)

        if payload.view_ids:
            params["view_ids"] = ",".join(str(view_id) for view_id in payload.view_ids)

        if payload.regenerate:
            params["regenerate"] = True

        if payload.only_base_config:
            params["only_base_config"] = True

        if payload.tracing_context:
            params["tracing_context"] = json.dumps(payload.tracing_context or {})

        return params

    async def fetch_cube_config(self, payload: CubePushConfigPayload):
        """Fetch cube configuration asynchronously"""
        logger.info(f"{self.log_prefix} Fetching cube config")
        params = self.build_request_params(payload)

        data = await self.client.request("GET", "/api/cube/config/md5", params=params, retries=4)
        remote_md5 = data["md5"]
        gzip_file = os.path.join(self.cube_dir, "cube.tar.gz")

        # Skip MD5 check when only_base_config is True to avoid stale config issues
        if payload.only_base_config:
            logger.info(
                f"{self.log_prefix} only_base_config=True, skipping MD5 check and forcing config fetch, remote md5: {remote_md5}"
            )
        else:
            local_md5 = await self.calculate_md5(gzip_file)
            if remote_md5 == local_md5:
                logger.info(f"{self.log_prefix} md5 is the same, skip fetch config, remote md5: {remote_md5}")
                return

        await self.client.request_file("GET", "/api/cube/config/gz", file_name=gzip_file, params=params)

        await asyncio.gather(
            asyncio.to_thread(self.remove_non_empty_dir, self.cube_connections_dir),
            asyncio.to_thread(self.remove_non_empty_dir, self.cube_projects_dir),
        )
        await self.tar_gzip_uncompress(gzip_file, self.cube_conf_dir)

        logger.info(f"{self.log_prefix} Cube config fetched successfully.")

    async def acquire_cube_lock(self, ttl: int = 20, lock_type: str = "compilation"):
        """Acquire a cube lock via API endpoint"""
        try:
            params = {"ttl": ttl, "lock_type": lock_type}
            data = await self.client.request("GET", "/api/cube/config/acquire-lock", params=params)
            success = data.get("success", False)
            logger.info(f"{self.log_prefix} Cube {lock_type} lock acquire result: {success}")
            return success
        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to acquire cube {lock_type} lock: {e}")
            return False

    async def release_cube_lock(self, lock_type: str = "compilation"):
        """Release a cube lock via API endpoint"""
        try:
            params = {"lock_type": lock_type}
            data = await self.client.request("GET", "/api/cube/config/release-lock", params=params)
            logger.info(f"{self.log_prefix} Successfully released cube {lock_type} lock - with response: {data}")
            return True
        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to release cube {lock_type} lock: {e}")
            return False

    async def check_cube_lock(self, lock_type: str = "compilation"):
        """Check if a cube lock is active via API endpoint"""
        try:
            params = {"lock_type": lock_type}
            data = await self.client.request("GET", "/api/cube/config/check-lock", params=params)
            is_locked = data.get("locked", False)
            logger.info(f"{self.log_prefix} Cube {lock_type} lock status: {is_locked}")
            return is_locked
        except Exception as e:
            logger.error(f"{self.log_prefix} Failed to check cube {lock_type} lock: {e}")
            return False

    async def get_cube_api_port(self):
        """Extract the host port for cube_api container using docker library"""
        host_port = await asyncio.to_thread(get_container_port, CUBE_CONTAINER_SUFFIX, "15433")

        if host_port:
            logger.info(f"{self.log_prefix} Found cube_api container port: {host_port}")
            return host_port

        logger.warning(f"{self.log_prefix} No cube_api container found or no port binding")
        return DEFAULT_CUBE_PORT  # fallback to default

    async def validate_sql_connection(self, project_id: int | None = None):
        """Validate CubeJS connection using psql command directly, fallback to API if psql not available"""
        if project_id:
            logger.info(f"{self.log_prefix} Validating sql connection for project {project_id}")
        else:
            logger.info(f"{self.log_prefix} Validating sql connection for all projects")

        # CubeJS connection parameters (using test credentials as in health monitor script)
        cube_host = "localhost"
        cube_port = await self.get_cube_api_port()  # Dynamically get the port from docker
        validate_user = "test:test"
        validate_pass = "test"
        validate_db = "test"

        logger.info(f"{self.log_prefix} Using cube_port: {cube_port}")

        try:
            # Run psql connection test with timeout using async subprocess
            env = os.environ.copy()
            env["PGPASSWORD"] = validate_pass

            process = await asyncio.create_subprocess_exec(
                "timeout",
                "10",
                "psql",
                "-h",
                cube_host,
                "-p",
                cube_port,
                "-U",
                validate_user,
                "-d",
                validate_db,
                "-c",
                "SELECT 1;",
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            try:
                _, stderr = await asyncio.wait_for(process.communicate(), timeout=15)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning(f"{self.log_prefix} CubeJS connection validation TIMEOUT")
                return {"success": False, "message": "CubeJS validation timeout"}

            if process.returncode == 0:
                logger.info(f"{self.log_prefix} CubeJS connection validation PASSED")
                return {"success": True, "message": "CubeJS connection validated successfully"}
            else:
                error_msg = stderr.decode() if stderr else "Connection failed"
                # Check if the error is due to missing psql command
                if ("failed to run command" in error_msg and "psql" in error_msg) or "command not found" in error_msg:
                    logger.info(f"{self.log_prefix} psql command not found, falling back to API validation")
                    return await self.validate_sql_connection_using_api(project_id)
                else:
                    logger.warning(f"{self.log_prefix} CubeJS connection validation FAILED: {error_msg}")
                    return {"success": False, "message": f"CubeJS validation failed: {error_msg}"}

        except Exception as e:
            exception_error_msg = str(e)
            error_msg = f"Failed to validate CubeJS connection: {exception_error_msg}"
            logger.error(f"{self.log_prefix} {error_msg}")
            # Check if the error is due to missing psql command
            if "failed to run command" in exception_error_msg and "psql" in exception_error_msg:
                logger.info(f"{self.log_prefix} psql command not found, falling back to API validation")
                return await self.validate_sql_connection_using_api(project_id)
            else:
                # Still return success=True for other errors to avoid unnecessary restarts
                return {"success": True, "message": f"CubeJS validation error but continuing: {error_msg}"}

    async def validate_sql_connection_using_api(self, project_id: int | None = None):
        """Validate SQL connection using API"""
        if project_id:
            logger.info(f"{self.log_prefix} Validating sql connection using API for project {project_id}")
            params = {"project_id": project_id}
        else:
            logger.info(f"{self.log_prefix} Validating sql connection using API for all projects")
            params = {}

        validation_data = await self.client.request("GET", VALIDATION_ENDPOINT, params=params, retries=4)
        return validation_data

    async def push_cube_config(self, payload: CubePushConfigPayload) -> None:
        """Main processing function for cube push config service."""
        logger.info(
            f"{self.log_prefix} Processing cube push config for env_id: {payload.env_id}, project_id: {payload.project_id}"
        )

        try:
            existing_env_file = await self.read_cube_conf_file(".env")
            logger.info(f"{self.log_prefix} existing env file: \n{existing_env_file}")

            await self.fetch_cube_config(payload)
            await self.download_cacert_pem()
            await self.fetch_cube_connections(payload)

            # Fetch updated env file from server (handles ClickHouse logic and change detection)
            if payload.project_id:
                env_update_result = await self.fetch_updated_env_file(payload, existing_env_file)

                # Use the env content directly from the server response
                new_env_file = env_update_result.get("env_content", existing_env_file)
                logger.info(f"{self.log_prefix} new env file: \n{new_env_file}")
                restart_needed = False

                # Check for general environment changes (now determined by server)
                if env_update_result.get("has_general_env_changes", False):
                    logger.info(f"{self.log_prefix} Server detected general env file changes, restart containers")
                    restart_needed = True
                    await self.restart_containers_with_lock(payload)

                # Check for ClickHouse changes (now determined by server)
                if env_update_result.get("has_clickhouse_changes", False):
                    logger.info(f"{self.log_prefix} Server detected ClickHouse changes, restart cube api container")
                    restart_needed = True
                    await self.restart_containers_with_lock(payload, restart_cube_api_only=True)

                # Wait for 10 seconds to ensure the container is restarted
                if restart_needed:
                    logger.info(
                        f"{self.log_prefix} Restarting cube api container, waiting for 10 seconds before validation"
                    )
                    await asyncio.sleep(10)
                else:
                    logger.info(f"{self.log_prefix} No restart needed because of no env file changes")

                validation_data = await self.validate_sql_connection(payload.project_id)
                logger.info(f"{self.log_prefix} Cube connection validation data: {validation_data}")
                if validation_data and validation_data.get("success"):
                    logger.info(f"{self.log_prefix} Successfully validated sql connection {validation_data}")
                else:
                    logger.info(f"{self.log_prefix} Failed to validate sql connection, restart cube api container")
                    restart_needed = True
                    await self.restart_containers_with_lock(payload, restart_cube_api_only=True)

                # Release cube compilation & restarting locks
                await self.release_cube_lock(lock_type="compilation")
                if restart_needed:
                    await self.release_cube_lock(lock_type="restarting")
            else:
                logger.info(f"{self.log_prefix} No project_id, skip env file update")

            logger.info(f"{self.log_prefix} Cube push config successful for env_id: {payload.env_id}")
        except Exception as e:
            logger.error(f"{self.log_prefix} Error processing cube push config for env_id {payload.env_id}: {e}")
            # raise for retry
            raise e


cube_push_config_service = CubePushConfigService()
