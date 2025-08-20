import ipaddress
import platform
import socket
from typing import Optional

import psutil
from loguru import logger
from pydantic import BaseModel


class DiskInfo(BaseModel):
    device: str
    mountpoint: str
    total: int


class HostInfo(BaseModel):
    os: str
    os_release: str
    os_arch: str
    cpu_cores: int
    memory_total: int
    disks: list[DiskInfo]
    python_version: str
    python_implementation: str
    linux_distribution: Optional[dict[str, str]] = None


class HostMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float


def get_disks() -> list[DiskInfo]:
    disks = []
    for part in psutil.disk_partitions():
        if "cdrom" in part.opts or part.fstype == "":
            continue
        usage = psutil.disk_usage(part.mountpoint)
        disks.append(
            DiskInfo(
                device=part.device,
                mountpoint=part.mountpoint,
                total=usage.total,
            )
        )
    return disks


def get_linux_distribution() -> Optional[dict[str, str]]:
    if platform.system() != "Linux":
        return None

    result = {}
    try:
        os_release_path = "/etc/os-release"
        with open(os_release_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    result[key] = value.strip('"')
    except Exception as e:
        logger.debug(f"Error reading /etc/os-release: {str(e)}")
        result = None
    return result


def get_host_info() -> HostInfo:
    return HostInfo(
        os=platform.system(),
        os_release=platform.release(),
        os_arch=platform.machine(),
        cpu_cores=psutil.cpu_count(logical=True),
        memory_total=psutil.virtual_memory().total,
        disks=get_disks(),
        python_version=platform.python_version(),
        python_implementation=platform.python_implementation(),
        linux_distribution=get_linux_distribution(),
    )


def get_hostname_ip() -> tuple[str, str]:
    """Get the hostname and IP address of the current machine."""
    hostname = socket.gethostname()

    local_ips = get_local_ips()
    if local_ips:
        ip_address = local_ips[0]
    else:
        raise RuntimeError("Failed to get the LAN IP address of the current machine")
    return hostname, ip_address


def _is_private_ip(ip: str) -> bool:
    address = ipaddress.ip_address(ip)
    return address.is_private


def _is_docker_interface(interface: str) -> bool:
    """Check if a network interface is a Docker virtual network interface."""
    docker_prefixes = ["docker", "br-", "veth", "lo"]
    return any(interface.startswith(prefix) for prefix in docker_prefixes)


def _is_loopback_ip(ip: str) -> bool:
    address = ipaddress.ip_address(ip)
    return address.is_loopback


def get_local_ips() -> list[str]:
    """Get a list of local IP addresses suitable for LAN communication."""
    local_ips = []

    # Get all network interfaces and their addresses
    addrs = psutil.net_if_addrs()

    for interface, addr_info in addrs.items():
        # Skip Docker virtual network interfaces
        if _is_docker_interface(interface):
            continue
        for addr in addr_info:
            # Check if the address is an IPv4 address and not a loopback address
            if addr.family == socket.AF_INET and not _is_loopback_ip(addr.address):
                # Check if the address is a private IP address
                if _is_private_ip(addr.address):
                    local_ips.append(addr.address)

    return local_ips


def get_host_metrics(path: str) -> HostMetrics:
    return HostMetrics(
        cpu_usage=psutil.cpu_percent(),
        memory_usage=psutil.virtual_memory().percent,
        disk_usage=psutil.disk_usage(path).percent,
    )
