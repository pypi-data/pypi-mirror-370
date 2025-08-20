import asyncio
import traceback
from typing import Any, Callable, Coroutine
from uuid import UUID

from loguru import logger

from recurvedata.agent._internal.schemas import TaskStatus, UpdateTaskInstanceStatus
from recurvedata.agent._internal.websocket.connector import WebSocketConnector
from recurvedata.agent._internal.websocket.schemas import MessageType, WebSocketMessage

TASK_RETRY_INTERVAL_SECONDS = 1


class TaskManager:
    """
    A Thread-safe task manager.
    """

    def __init__(self):
        self._task_registry: dict[UUID, asyncio.Task] = dict()
        self._task_lock = asyncio.Lock()

    async def create(
        self,
        task_id: UUID,
        handler: Callable[[WebSocketMessage, WebSocketConnector], Coroutine[Any, Any, Any]],
        websocket_message: WebSocketMessage,
        ws_connector: WebSocketConnector,
    ) -> None:
        """
        Create a new task with retry mechanism.
        """
        async with self._task_lock:
            task = asyncio.create_task(self._run_with_retry(handler, websocket_message, ws_connector))
            task.add_done_callback(lambda t: self._on_done(task_id, t, websocket_message, ws_connector))
            self._task_registry[task_id] = task

    async def _run_with_retry(
        self,
        handler: Callable[[WebSocketMessage, WebSocketConnector], Coroutine[Any, Any, Any]],
        websocket_message: WebSocketMessage,
        ws_connector: WebSocketConnector,
    ) -> None:
        # all attempts = max_retries + 1
        retries = 0
        last_exception = None

        while retries <= websocket_message.max_retries:
            retries += 1
            try:
                # Run handler with timeout
                result = await asyncio.wait_for(
                    handler(websocket_message, ws_connector),
                    timeout=websocket_message.max_duration,
                )
                return result
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.error(
                    f"Task {websocket_message.message_id} timed out after {websocket_message.max_duration} seconds (attempt {retries}/{websocket_message.max_retries + 1})"
                )
            except Exception as e:
                last_exception = e
                logger.error(
                    f"Task {websocket_message.message_id} failed (attempt {retries}/{websocket_message.max_retries + 1}): {e}",
                )
                traceback.print_exc()

            # if there are more attempts, wait for a while before the next attempt
            if retries <= websocket_message.max_retries:
                await asyncio.sleep(TASK_RETRY_INTERVAL_SECONDS)

        # all attempts failed, raise the last exception
        if last_exception:
            raise last_exception

    def _on_done(
        self,
        task_id: UUID,
        task: asyncio.Task,
        websocket_message: WebSocketMessage,
        ws_connector: WebSocketConnector,
    ) -> None:
        self._task_registry.pop(task_id, None)

        try:
            result = task.result()
            logger.info(f"Task {task_id} has been completed: {result}")
        except Exception as e:
            logger.error(f"Task {task_id} has been failed: {e}")
            try:
                # send task failed to server
                asyncio.create_task(
                    ws_connector.send_json(
                        WebSocketMessage(
                            type=MessageType.RESULT,
                            payload=UpdateTaskInstanceStatus(
                                status=TaskStatus.FAILED,
                                error={"reason": str(e), "traceback": traceback.format_exc()},
                            ).model_dump(),
                            reply_to=websocket_message.message_id,
                            message_id=websocket_message.message_id,
                        ).model_dump()
                    )
                )
            except Exception as e:
                logger.error(f"Failed to update task status to failed: {e}")

    async def cancel_task(self, task_id: UUID) -> None:
        async with self._task_lock:
            task = self._task_registry.pop(task_id, None)

        if task:
            task.cancel()
            try:
                await task
                logger.info(f"Task {task_id} has been cancelled")
            except asyncio.CancelledError as e:
                logger.warning(f"Cancel task {task_id} failed: {e}")
        else:
            logger.warning(f"Task {task_id} not found")


global_task_manager = TaskManager()
