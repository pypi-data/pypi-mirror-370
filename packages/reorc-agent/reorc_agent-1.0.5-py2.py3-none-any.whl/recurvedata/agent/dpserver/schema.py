from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DPServerResponseModel(BaseModel):
    ok: bool
    error: Any | None
    data: Any | None


class DPServerRequestPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    request_timeout: int = 300
    server_host: str
    path: str
    method: str
    params: dict | None = None
    # json is an attr in BaseModel, so we use json_data
    json_data: dict | None = Field(None, alias="json")
    data: dict | None = None
