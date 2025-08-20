from enum import Enum


class RecurveEnum(str, Enum):
    """Base Enum class for Recurve."""

    def __str__(self) -> str:
        return str.__str__(self)


class MessageType(RecurveEnum):
    # DP -> CP:
    HEARTBEAT = "heartbeat"
    REPORT_HOST_INFO = "report-host-info"
    RESULT = "result"
    TASK_ACK = "task-ack"
    # HTTP over Websocket
    HTTP_RESPONSE = "http-response"
    # SQL over Websocket
    CUBE_SQL_RESPONSE = "cube-sql-response"

    # CP -> DP:
    HEARTBEAT_REQUEST = "heartbeat-request"
    WORKER_MANAGEMENT = "worker-management"
    BUSINESS = "business"
    CANCEL = "cancel"
    # send source code to agent to execute, CP -> DP
    SOURCE_CODE_EXEC = "source-code-exec"
    # HTTP over Websocket
    HTTP_REQUEST = "http-request"
    # SQL over Websocket
    CUBE_SQL_REQUEST = "cube-sql-request"
