import asyncio
import os

from loguru import logger

from recurvedata.agent._internal.client import AgentClient
from recurvedata.agent._internal.docker import get_containers_batch
from recurvedata.agent._internal.schemas import CubeRestartServicePayload
from recurvedata.agent.config import CONFIG, RECURVE_HOME

# Configuration constants
MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds
CONTAINER_STARTUP_WAIT = 5  # seconds
CUBE_CONTAINER_SUFFIX = "_cube_api_1"
VALIDATION_ENDPOINT = "/api/cube/config/validate-sql-connection"


class CubeRestartService:
    """Service class for handling cube restart operations"""

    def __init__(self):
        self.client = AgentClient(CONFIG)
        self.cube_dir = os.path.join(RECURVE_HOME, "cube")
        self.cube_conf_dir = os.path.join(self.cube_dir, "conf")
        self.log_prefix = "[cube-restart-service]"

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

    async def restart_cube_containers(self, payload: CubeRestartServicePayload, restart_cube_api_only: bool = True):
        """Restart cube containers for the given environment asynchronously."""
        if not payload.container_names:
            logger.warning(f"{self.log_prefix} No container names provided for env_id: {payload.env_id}")
            return

        logger.info(
            f"{self.log_prefix} Starting cube container restart for env_id: {payload.env_id}, tenant: {payload.tenant_id}"
        )

        # Filter containers that need to be restarted
        containers_to_restart = self.filter_containers_to_restart(payload.container_names, restart_cube_api_only)

        if not containers_to_restart:
            logger.info(f"{self.log_prefix} No containers to restart for env_id: {payload.env_id}")
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

        logger.info(f"{self.log_prefix} Cube container restart completed for env_id: {payload.env_id}")

    async def validate_cube_connection_after_restart(self, payload: CubeRestartServicePayload) -> bool:
        """Validate cube connection after restart to ensure the restart was successful."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    f"{self.log_prefix} Cube connection validation attempt {attempt}/{MAX_RETRIES} for env_id: {payload.env_id}"
                )

                validation_data = await self.client.request(
                    "GET",
                    VALIDATION_ENDPOINT,
                    params={},
                    retries=4,
                )

                logger.info(f"{self.log_prefix} Cube connection validation data: {validation_data}")

                if validation_data and validation_data.get("success"):
                    logger.info(
                        f"{self.log_prefix} Cube connection validation successful for env_id: {payload.env_id} on attempt {attempt}"
                    )
                    return True

                logger.warning(
                    f"{self.log_prefix} Cube connection validation failed for env_id: {payload.env_id} on attempt {attempt}"
                )

                if attempt < MAX_RETRIES:
                    logger.info(f"{self.log_prefix} Retrying in {RETRY_DELAY} seconds...")
                    await asyncio.sleep(RETRY_DELAY)

            except Exception as e:
                logger.error(
                    f"{self.log_prefix} Error validating cube connection for env_id {payload.env_id} on attempt {attempt}: {e}"
                )
                if attempt < MAX_RETRIES:
                    logger.info(f"{self.log_prefix} Retrying in {RETRY_DELAY} seconds...")
                    await asyncio.sleep(RETRY_DELAY)

        logger.error(
            f"{self.log_prefix} Cube connection validation failed for env_id: {payload.env_id} after {MAX_RETRIES} attempts"
        )
        return False

    async def restart_cube_service(self, payload: CubeRestartServicePayload) -> None:
        """Main processing function for cube restart service."""
        logger.info(
            f"{self.log_prefix} Processing cube restart for env_id: {payload.env_id}, tenant: {payload.tenant_id}"
        )

        try:
            # Restart cube containers
            await self.restart_cube_containers(payload)

            # Wait a bit for containers to fully start
            await asyncio.sleep(CONTAINER_STARTUP_WAIT)

            # Validate connection after restart
            is_connection_valid = await self.validate_cube_connection_after_restart(payload)

            if is_connection_valid:
                logger.info(f"{self.log_prefix} Cube restart successful for env_id: {payload.env_id}")
            else:
                logger.warning(
                    f"{self.log_prefix} Cube restart completed but connection validation failed for env_id: {payload.env_id}"
                )
        except Exception as e:
            logger.error(f"{self.log_prefix} Error processing cube restart for env_id {payload.env_id}: {e}")
            # raise for retry
            raise e


cube_restart_service = CubeRestartService()
