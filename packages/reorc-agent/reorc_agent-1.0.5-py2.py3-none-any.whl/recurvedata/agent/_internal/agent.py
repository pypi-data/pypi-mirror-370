from functools import partial
from uuid import UUID, uuid4

import anyio
from loguru import logger
from typing_extensions import Self

from .._version import VERSION
from ..config import CONFIG, AgentConfig
from ..exceptions import UnauthorizedError
from . import host, worker
from .client import AgentClient
from .schemas import AgentHostInfo, Heartbeat, LoginPayload
from .service_loop import critical_service_loop
from .websocket import WebSocketConnector
from .websocket.callbacks import handle_websocket_message, on_connect, on_disconnect, on_error
from .websocket.schemas import MessageType, WebSocketMessage


class Agent:
    _config: AgentConfig
    client: AgentClient
    ws_connector: WebSocketConnector

    def __init__(self, config: AgentConfig):
        self.set_config(config)

    @classmethod
    def default(cls) -> Self:
        return cls(CONFIG)

    @property
    def config(self) -> AgentConfig:
        return self._config

    def set_config(self, value: AgentConfig):
        self._config = value
        self.client = AgentClient(value)
        self.ws_connector = WebSocketConnector(value)

    @property
    def id(self) -> UUID:
        return self.config.agent_id

    @property
    def has_logged_in(self) -> bool:
        return self.config.is_valid() and self.config.logged_in

    # ----------------------------- #
    # Login and Logout via REST API
    # ----------------------------- #
    async def login(self, encoded_token: str):
        self.config.set_auth_token(encoded_token)
        # update the client with the new config (server_url and token)
        self.client.set_config(self.config)

        hostname, ip_address = host.get_hostname_ip()
        await self.client.login(
            LoginPayload(
                tenant_domain=self.config.tenant_domain,
                agent_id=self.id,
                auth_token=self.config.token.get_secret_value(),
                hostname=hostname,
                ip_address=ip_address,
                agent_version=VERSION,
                host_info=host.get_host_info(),
            )
        )
        self.config.logged_in = True
        self.config.save()

    async def logout(self):
        await self.client.logout(agent_id=self.id)
        self.config.clear_auth_token()
        self.config.logged_in = False
        self.client.set_config(self.config)
        self.config.save()

    # ----------------------------- #
    # WebSocket Communication
    # ----------------------------- #
    async def report_host_info(self):
        hostname, ip_address = host.get_hostname_ip()
        payload = AgentHostInfo(
            hostname=hostname,
            ip_address=ip_address,
            agent_version=VERSION,
            host_info=host.get_host_info(),
        )
        message = WebSocketMessage(
            type=MessageType.REPORT_HOST_INFO,
            payload=payload.model_dump(mode="json"),
            message_id=str(uuid4()),
        )
        await self.ws_connector.send_json(message.model_dump())

    async def send_heartbeat(self):
        logger.info("Sending heartbeat...")

        if not self.ws_connector.is_connected:
            logger.error("WebSocket connection is not established...")
            # don't raise exception, don't reconnect, just return and let the listen_loop reconnect
            return

        path = worker.get_docker_root_dir()
        payload = Heartbeat(
            agent_id=self.id,
            metrics=host.get_host_metrics(path=path),
            service_status=worker.get_service_status(),
        )
        message = WebSocketMessage(
            type=MessageType.HEARTBEAT,
            payload=payload.model_dump(mode="json"),
            message_id=str(uuid4()),
        )
        await self.ws_connector.send_json(message.model_dump())

    async def sync_with_server(self):
        try:
            await self.send_heartbeat()
        except UnauthorizedError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to sync with server: {e}")

    async def start(self):
        try:
            async with anyio.create_task_group() as tg:
                logger.info("Establishing WebSocket connection...")
                await self.ws_connector.connect()

                # set callbacks
                self.ws_connector.set_callbacks(
                    on_receive_message=handle_websocket_message,
                    on_connect=on_connect,
                    on_disconnect=on_disconnect,
                    on_error=on_error,
                )

                # send host info first
                await self.report_host_info()
                # Wait for an initial heartbeat to configure the worker
                await self.sync_with_server()

                # start listening and auto call callback on receive message
                logger.info("Starting WebSocket message listening...")
                tg.start_soon(self.ws_connector.listen_loop)

                logger.info("Start sending heartbeats.")
                tg.start_soon(
                    partial(
                        critical_service_loop,
                        workload=self.send_heartbeat,
                        interval=self.config.heartbeat_interval,
                        printer=logger.info,
                        jitter_range=0.3,
                        backoff=4,
                    )
                )
        except ExceptionGroup as eg:
            # Check if ExceptionGroup contains UnauthorizedError
            for exc in eg.exceptions:
                if isinstance(exc, UnauthorizedError):
                    logger.info("Agent stopped due to unauthorized access")
                    # Re-raise UnauthorizedError for upper layer handling
                    raise UnauthorizedError("Unauthorized, please re-login with a valid token.") from exc
            # If not UnauthorizedError, re-raise the exception
            raise

    async def close(self):
        """Close agent and clean up resources"""
        logger.info("Closing agent...")

        # Close WebSocket connection first
        if self.ws_connector and self.ws_connector.is_connected:
            try:
                await self.ws_connector.disconnect()
            except Exception as e:
                logger.debug(f"Error closing WebSocket: {e}")

        # Close HTTP client
        if self.client:
            try:
                await self.client.close()
            except Exception as e:
                logger.debug(f"Error closing HTTP client: {e}")

        logger.info("Agent closed successfully")
