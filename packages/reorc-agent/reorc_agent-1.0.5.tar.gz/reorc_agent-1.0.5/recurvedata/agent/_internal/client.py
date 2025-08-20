from __future__ import annotations

import asyncio
import json
from typing import Any, TypeVar
from uuid import UUID

import httpx
from loguru import logger
from pydantic import BaseModel

from .._version import VERSION
from ..config import AgentConfig
from ..exceptions import APIError, MaxRetriesExceededException, UnauthorizedError
from .schemas import LoginPayload

ResponseModelType = TypeVar("ResponseModelType", bound=BaseModel)


class AgentClient:
    _config: AgentConfig
    _client: httpx.AsyncClient

    def __init__(self, config: AgentConfig):
        self.set_config(config)

    def set_config(self, config: AgentConfig):
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.server_url,
            timeout=config.request_timeout,
            headers={"User-Agent": f"RecurveAgent/{VERSION}"},
        )

    def prepare_header(self, kwargs: dict):
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._config.agent_id}:{self._config.token.get_secret_value()}"
        headers["X-Tenant-Domain"] = self._config.tenant_domain
        kwargs["headers"] = headers

    async def request(
        self,
        method: str,
        path: str,
        response_model_class: type[ResponseModelType] | None = None,
        retries: int = 1,
        **kwargs,
    ) -> Any:
        self.prepare_header(kwargs)

        last_error = None
        for attempt in range(retries):
            try:
                resp = await self._client.request(method, path, **kwargs)
                duration = resp.elapsed.total_seconds() * 1000
                logger.debug(f"[{method}] {resp.url} ({resp.status_code}), elapsed: {duration:.2f}ms, {kwargs}")

                resp.raise_for_status()
                resp_content = resp.json()

                # TODO(yangliang): handle errors more gracefully
                if resp_content["code"] != "0":
                    raise APIError(f"API request failed: {resp_content['msg']}")

                if response_model_class is not None:
                    return response_model_class.model_validate(resp_content["data"])
                return resp_content["data"]
            except httpx.HTTPStatusError as e:
                logger.debug(
                    f"HTTP error on attempt {attempt + 1} for url '{e.request.url}' :"
                    f" {e.response.status_code} - {e.response.text}"
                )
                last_error = e
                if e.response.status_code == 401:
                    raise UnauthorizedError("Unauthorized, please check your agent_id and token")
            except httpx.RequestError as e:
                logger.debug(f"Request error on attempt {attempt + 1} for url '{e.request.url}': {e}")
                last_error = e

            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)  # Exponential backoff
            else:
                raise MaxRetriesExceededException(
                    f"Failed to complete {method} request to {path} after {retries} attempts"
                ) from last_error

    async def request_file(
        self,
        method: str,
        path: str,
        file_name: str,
        retries: int = 1,
        **kwargs,
    ) -> Any:
        self.prepare_header(kwargs)

        last_error = None
        for attempt in range(retries):
            try:
                resp = await self._client.request(method, path, **kwargs)
                duration = resp.elapsed.total_seconds() * 1000
                logger.debug(f"[{method}] {resp.url} ({resp.status_code}), elapsed: {duration:.2f}ms, {kwargs}")
                resp.raise_for_status()
                try:
                    resp_content = resp.json()

                    if "code" in resp_content and resp_content["code"] != "0":
                        raise APIError(f"API request failed: {resp_content['msg']}\n{resp_content.get('data')}")
                except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                    pass

                with open(file_name, "wb") as f:
                    f.write(resp.content)
                return

            except httpx.HTTPStatusError as e:
                logger.debug(
                    f"HTTP error on attempt {attempt + 1} for url '{e.request.url}' :"
                    f" {e.response.status_code} - {e.response.text}"
                )
                last_error = e
                if e.response.status_code == 401:
                    raise UnauthorizedError("Unauthorized, please check your agent_id and token")
            except httpx.RequestError as e:
                logger.debug(f"Request error on attempt {attempt + 1} for url '{e.request.url}': {e}")
                last_error = e

            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)  # Exponential backoff
            else:
                raise MaxRetriesExceededException(
                    f"Failed to complete {method} request to {path} after {retries} attempts"
                ) from last_error

    async def close(self):
        await self._client.aclose()

    # Login and Logout dependent with websocket connection
    async def login(self, payload: "LoginPayload"):
        resp = await self._client.post("/api/agents/login", json=payload.model_dump(mode="json"))
        if resp.status_code == 401:
            raise UnauthorizedError("Unauthorized, please check your agent_id and token")
        resp.raise_for_status()

        # temporary solution
        resp_content = resp.json()
        if resp_content["code"] != "0":
            raise APIError(f"API request failed: {resp_content['msg']}")

    async def logout(self, agent_id: UUID):
        await self.request("POST", "/api/agents/logout", params={"agent_id": agent_id})
