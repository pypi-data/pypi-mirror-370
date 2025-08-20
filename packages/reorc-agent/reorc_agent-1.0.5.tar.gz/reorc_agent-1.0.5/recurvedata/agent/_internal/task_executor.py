import asyncio
import base64
import functools
import json
import logging
import os
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from ..config import RECURVE_HOME
from .schemas import SourceCodeExecPayload, TaskResultPayload, TaskStatus
from .utils import utcnow

if TYPE_CHECKING:
    from logging import Logger


@dataclass
class TaskExecutor:
    task_heartbeat_interval: float = 1
    task_retry_interval: int = 5
    subprocess_pid: int | None = None

    async def execute(self, task: "SourceCodeExecPayload") -> "TaskResultPayload":
        start_time = time.time()
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Task {task.task_instance_id} started in working directory: {temp_dir}")
            result = await self._execute_in_tempdir(task, temp_dir)

        logger.info(f"Task {task.task_instance_id} completed in {time.time() - start_time:.2f} seconds.")
        return result

    async def _execute_in_tempdir(self, task: "SourceCodeExecPayload", workdir: str) -> "TaskResultPayload":
        task_instance_id = task.task_instance_id

        cmd_args, output_file = self._prepare_execution_context(task, workdir)

        log_queue = asyncio.Queue()
        executor_logger = _ExecutorLogger(log_queue)

        try:
            await executor_logger.info(f"Executing task: {task_instance_id}")

            task_logger = _setup_task_logger(task_instance_id)
            await self.execute_in_subprocess(
                *cmd_args,
                cwd=workdir,
                log_queue=log_queue,
                timeout=task.max_duration,
                task_logger=task_logger,
            )

            # success, read result and update status
            result = None
            if output_file.exists():
                result = json.loads(output_file.read_text())

            await executor_logger.info(f"Task {task_instance_id} completed successfully.")

            return TaskResultPayload(
                status=TaskStatus.SUCCESS,
                result=result,
                logs=await self.drain_queue(log_queue),
            )
        except (subprocess.CalledProcessError, TimeoutError) as e:
            await executor_logger.error(f"Task {task_instance_id} failed: {e}")
            # raise for outside retry
            raise
        except Exception as e:
            await executor_logger.error(f"Task {task_instance_id} failed: {e}")
            return TaskResultPayload(
                status=TaskStatus.FAILED,
                error={"reason": str(e), "traceback": traceback.format_exc()},
                logs=await self.drain_queue(log_queue),
            )

    @staticmethod
    def _prepare_execution_context(task: "SourceCodeExecPayload", workdir: str) -> tuple[tuple[str, ...], Path]:
        script = Path(workdir) / f"handler.{task.handler_format}"
        script.write_bytes(base64.b64decode(task.handler_code))

        input_file = Path(workdir) / "payload.json"
        input_file.write_text(json.dumps(task.payload, indent=2))

        output_file = Path(workdir) / "result.json"

        # python /path/to/handler.py --input /path/to/payload.json --output /path/to/result.json
        cmd_args = (
            str(script),
            "--input",
            str(input_file),
            "--output",
            str(output_file),
        )
        return cmd_args, output_file

    async def execute_in_subprocess(
        self,
        *args: str,
        cwd: str,
        log_queue: asyncio.Queue[str],
        timeout: int,
        task_logger: "Logger",
    ):
        env = os.environ.copy()
        env["RECURVE_HOME"] = RECURVE_HOME

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            *args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.subprocess_pid = process.pid
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    self.read_stream(process.stdout, log_queue, task_logger),
                    self.read_stream(process.stderr, log_queue, task_logger),
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"Subprocess timed out after {timeout} seconds, killing it.")
            process.kill()
            await process.wait()
            raise TimeoutError(f"Subprocess timed out after {timeout} seconds")

        rc = await process.wait()
        if rc < 0:
            signal_number = -rc
            signal_name = signal.Signals(signal_number).name
            msg = f"Subprocess was terminated by signal: {signal_name} (signal number: {signal_number})"
            logger.warning(msg)
            await log_queue.put(_format_log_message(msg))
        elif rc != 0:
            raise subprocess.CalledProcessError(rc, "python")

    @staticmethod
    async def read_stream(stream: asyncio.StreamReader, log_queue: asyncio.Queue[str], task_logger: "Logger"):
        while True:
            line = await stream.readline()
            if not line:
                break
            log_message = line.decode().strip()
            await log_queue.put(_format_log_message(log_message))
            task_logger.info(log_message)  # Print the log message to the console

    @staticmethod
    async def drain_queue(log_queue: asyncio.Queue[str]) -> list[str]:
        logs: list[str] = []
        while not log_queue.empty():
            logs.append(await log_queue.get())
        return logs


@dataclass
class _ExecutorLogger:
    log_queue: asyncio.Queue[str]

    async def info(self, msg: str):
        logger.info(msg)
        await self.log_queue.put(_format_log_message(msg))

    async def warning(self, msg: str):
        logger.warning(msg)
        await self.log_queue.put(_format_log_message(msg))

    async def error(self, msg: str):
        logger.error(msg)
        await self.log_queue.put(_format_log_message(msg))


def _format_log_message(msg: str) -> str:
    return f"{utcnow()} | {msg}"


@functools.lru_cache(maxsize=20)
def _setup_task_logger(task_id: int) -> "Logger":
    task_logger = logging.getLogger(f"task-{task_id}")
    task_logger.handlers = []
    task_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(name)s] | %(message)s")
    handler.setFormatter(formatter)
    task_logger.addHandler(handler)
    return task_logger
