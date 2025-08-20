"""
This module contains the callbacks for the WebSocket connection.
They will be registered to the WebSocketConnector's `on_xxx` callbacks.

Message processing flow:
ws_connector -> on_receive_message -> handle_websocket_message -> message_handlers -> handle
"""

from uuid import uuid4

from loguru import logger
from pydantic import ValidationError

from recurvedata.agent._internal.schemas import TaskInstanceInfo, TaskStatus, UpdateTaskInstanceStatus
from recurvedata.agent._internal.task_manager import global_task_manager
from recurvedata.agent._internal.websocket.connector import WebSocketConnector
from recurvedata.agent._internal.websocket.enums import MessageType
from recurvedata.agent._internal.websocket.message_handlers import registry
from recurvedata.agent._internal.websocket.schemas import WebSocketMessage


async def handle_websocket_message(message: str, ws_connector: WebSocketConnector):
    """
    Handle incoming WebSocket messages,
    used for `on_receive_message` callback.
    """
    try:
        websocket_message = WebSocketMessage.model_validate_json(message)

        if websocket_message.type is None:
            logger.error(f"Unknown WebSocket message type: {message}")
            return

        # get handler by message type
        handler = registry.get_handler(websocket_message.type)
        if handler is None:
            logger.error(f"Unknown WebSocket message type: {websocket_message.type}")
            return

        task_id = str(uuid4())
        # report task is running
        await ws_connector.send_json(
            WebSocketMessage(
                type=MessageType.TASK_ACK,
                payload=UpdateTaskInstanceStatus(
                    status=TaskStatus.RUNNING,
                    info=TaskInstanceInfo(task_id=task_id),
                ).model_dump(),
                message_id=websocket_message.message_id,
                reply_to=websocket_message.message_id,
            ).model_dump()
        )

        # handle message in a new task
        await global_task_manager.create(task_id, handler.handle, websocket_message, ws_connector)

    except ValidationError as e:
        logger.error(f"Failed to parse WebSocket message: {e}")
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")


async def on_connect():
    """
    Callback function for WebSocket connection established.
    """
    logger.info("WebSocket connection established.")


async def on_disconnect():
    """
    Callback function for WebSocket connection closed.
    """
    logger.info("WebSocket connection closed.")


async def on_error(error: Exception):
    """
    Callback function for WebSocket connection error.
    """
    logger.error(f"WebSocket connection error: {error}")
