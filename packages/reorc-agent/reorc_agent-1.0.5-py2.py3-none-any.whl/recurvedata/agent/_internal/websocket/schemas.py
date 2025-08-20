from datetime import datetime

from pydantic import BaseModel

from .enums import MessageType


class WebSocketMessage(BaseModel):
    type: MessageType
    payload: dict | None = None
    message_id: str | None = None
    reply_to: str | None = None
    sending_time: datetime | None = None
    max_retries: int = 0
    max_duration: int = 30
