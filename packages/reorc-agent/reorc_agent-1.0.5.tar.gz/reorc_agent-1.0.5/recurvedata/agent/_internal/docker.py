import asyncio

import docker
from docker import DockerClient
from loguru import logger

# Global docker client instance
docker_client: DockerClient = docker.from_env()


def reset_docker_client() -> DockerClient:
    """Reset the global Docker client instance (useful for testing or reconnection)"""
    global docker_client
    docker_client = docker.from_env()
    return docker_client


async def get_container(container_name: str):
    """Get Docker container by name asynchronously"""
    try:
        container = await asyncio.to_thread(docker_client.containers.get, container_name)
        return container
    except Exception as e:
        raise ValueError(f"Container {container_name} not found: {e}")


async def get_containers_batch(container_names: list[str]) -> dict[str, any]:
    """Get multiple containers by names asynchronously, returns a dict mapping name to container"""
    if not container_names:
        return {}

    # Get all containers, then match by name
    all_containers = await asyncio.to_thread(docker_client.containers.list, all=True)
    container_map = {container.name: container for container in all_containers}

    containers = {}
    failed_containers = []

    for container_name in container_names:
        if container_name in container_map:
            containers[container_name] = container_map[container_name]
        else:
            failed_containers.append(container_name)

    if failed_containers:
        logger.warning(f"Containers not found: {failed_containers}")

    return containers


def get_container_port(container_name_suffix: str, internal_port: str) -> str | None:
    """Get host port for a container by name suffix and internal port"""
    try:
        # Get all containers and find container by suffix
        all_containers = docker_client.containers.list(all=True)

        for container in all_containers:
            if container.name.endswith(container_name_suffix):
                # Get container info including port bindings
                container_info = container.attrs
                ports = container_info.get("NetworkSettings", {}).get("Ports", {})

                # Look for port binding for the specified internal port
                port_binding = ports.get(f"{internal_port}/tcp")
                if port_binding:
                    # port_binding format: [{'HostIp': '0.0.0.0', 'HostPort': '15433'}]
                    for binding in port_binding:
                        if binding.get("HostIp") == "0.0.0.0":
                            host_port = binding.get("HostPort")
                            if host_port:
                                return host_port

                    # If no specific binding found, try to get any available port
                    if len(port_binding) > 0:
                        host_port = port_binding[0].get("HostPort")
                        if host_port:
                            return host_port

        return None
    except Exception as e:
        logger.error(f"Error getting container port: {e}")
        return None
