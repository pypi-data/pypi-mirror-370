from typing import Any

from recurvedata.agent._internal.client import AgentClient, ResponseModelType
from recurvedata.agent.config import AgentConfig
from recurvedata.agent.dpserver.schema import DPServerRequestPayload, DPServerResponseModel
from recurvedata.agent.exceptions import APIError


class DPServerClient(AgentClient):
    async def request(
        self,
        method: str,
        path: str,
        response_model_class: type[ResponseModelType] | None = None,
        **kwargs,
    ) -> Any:
        """
        Compared with super().request, this function has no retry logic,
        to avoid all exception type is MaxRetriesExceededException
        """
        self.prepare_header(kwargs)
        resp = await self._client.request(method, path, **kwargs)
        resp.raise_for_status()
        resp_content = resp.json()

        if "code" in resp_content and resp_content["code"] != "0":
            raise APIError(f"API request failed: {resp_content['msg']}\n{resp_content.get('data')}")

        if response_model_class is not None:
            if "code" in resp_content:
                return response_model_class.model_validate(resp_content["data"])
            return response_model_class.model_validate(resp_content)
        return resp_content.get("data")


def prepare_request_kwargs(payload: DPServerRequestPayload) -> dict:
    """Prepare kwargs for HTTP request from payload"""
    kwargs = {}
    for key in ["params", "data"]:
        value = getattr(payload, key)
        if value is not None:
            kwargs[key] = value

    # Handle json field separately due to alias
    if payload.json_data is not None:
        kwargs["json"] = payload.json_data

    return kwargs


async def request_dpserver(payload: DPServerRequestPayload) -> DPServerResponseModel:
    """
    Process a dpserver request asynchronously.
    This function can be called from websocket message handlers.

    Args:
        payload: The request payload containing server_host, path, method, etc.

    Returns:
        DPServerResponseModel: The response data from dpserver
    """
    config = AgentConfig.load()
    config.server_host = payload.server_host
    config.request_timeout = payload.request_timeout
    client = DPServerClient(config)

    kwargs = prepare_request_kwargs(payload)

    data = await client.request(
        method=payload.method,
        path=payload.path,
        response_model_class=DPServerResponseModel,
        **kwargs,
    )

    return data
