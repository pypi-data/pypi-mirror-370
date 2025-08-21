from abc import ABC
from enum import Enum
from typing_extensions import Union, Any, Literal, List, Annotated, Optional, Dict, Set
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, field_serializer
import datetime
import uuid

from openai.types.responses import ToolParam, ResponseInputItemParam, ResponseInputContentParam
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionContentPartParam
from openai.types.chat.chat_completion_tool_param import (
    ChatCompletionFunctionToolParam,
)
from openai.types.chat.chat_completion_message_function_tool_call_param import (
    ChatCompletionMessageFunctionToolCallParam,
)

from openai.types.shared_params.function_definition import (
    FunctionParameters,
    FunctionDefinition,
)

from agentlin.code_interpreter.types import Block


ContentData = ChatCompletionContentPartParam  # {"type": "text", "text": ""}
DialogData = ChatCompletionMessageParam  # {"role": "user", "content": "" | [ContentData]}
ToolData = ChatCompletionFunctionToolParam  # {"type": "function", "function": FunctionDefinition}

ResponsesContentData = ResponseInputContentParam  # {"type": "input_text", "text": ""}
ResponsesDialogData = ResponseInputItemParam  # {"type": "message", "role": "user", "content": "" | [ContentData]}
ResponsesToolData = ToolParam  # {"type": "function", "name": ...FunctionDefinition}

BlockData = Block
ToolCallContentData = ChatCompletionMessageFunctionToolCallParam

ToolParams = Dict[str, Any]

class ToolResult(BaseModel):
    message_content: list[dict] = []
    block_list: list[dict] = []
    key: Optional[str] = None

    def append_content(self, content: ContentData):
        """Append content to the message_content list."""
        self.message_content.append(content)

    def append_block(self, block: Block):
        """Append block to the block_list."""
        self.block_list.append(block)

    def extend_content(self, content_list: List[ContentData]):
        """Extend message_content with a list of ContentData."""
        self.message_content.extend(content_list)

    def extend_blocks(self, block_list: List[Block]):
        """Extend block_list with a list of Block."""
        self.block_list.extend(block_list)

    def extend_result(self, other: "ToolResult"):
        """Extend this ToolResult with another ToolResult."""
        self.message_content.extend(other.message_content)
        self.block_list.extend(other.block_list)


def sanitize_parameters(schema: Optional[FunctionDefinition]) -> None:
    _sanitize_parameters(schema, set())


def _sanitize_parameters(schema: Optional[FunctionDefinition], visited: Set[int]) -> None:
    if not schema or id(schema) in visited:
        return
    visited.add(id(schema))

    if "anyOf" in schema:
        schema.pop("default", None)
        for sub in schema["anyOf"]:
            if isinstance(sub, dict):
                _sanitize_parameters(sub, visited)

    if "items" in schema and isinstance(schema["items"], dict):
        _sanitize_parameters(schema["items"], visited)

    if "properties" in schema:
        for value in schema["properties"].values():
            if isinstance(value, dict):
                _sanitize_parameters(value, visited)

    if schema.get("type") == "string" and "format" in schema:
        if schema["format"] not in ("enum", "date-time"):
            schema["format"] = None


class BaseTool(ABC):
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        parameters: FunctionParameters,
        strict: bool = True,
    ):
        self.name = name
        self.title = title
        self.description = description
        self.parameters = parameters or {}
        self.strict = strict or True
        self.schema = FunctionDefinition(
            name=name,
            description=description,
            parameters=parameters,
            strict=strict,
        )

    @property
    def function_tool_schema(self) -> ToolData:
        return ToolData(
            type="function",
            function=self.schema,
        )

    async def execute(self, params: ToolParams) -> ToolResult:
        # Implement the tool's logic here
        raise NotImplementedError


class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"


class TaskStatus(BaseModel):
    state: TaskState
    payload: Any = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @field_serializer("timestamp")
    def serialize_dt(self, dt: datetime.datetime, _info):
        return dt.isoformat()


class Task(BaseModel):
    id: str
    sessionId: Optional[str] = None
    status: TaskStatus
    metadata: Optional[dict[str, Any]] = None


class TaskStatusUpdateEvent(BaseModel):
    id: str
    status: TaskStatus
    final: bool = False
    metadata: Optional[dict[str, Any]] = None


class TaskArtifactUpdateEvent(BaseModel):
    id: str
    metadata: Optional[dict[str, Any]] = None


class AuthenticationInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    schemes: List[str]
    credentials: Optional[str] = None


class PushNotificationConfig(BaseModel):
    url: str
    token: Optional[str] = None
    authentication: Optional[AuthenticationInfo] = None


class TaskIdParams(BaseModel):
    id: str
    metadata: Optional[dict[str, Any]] = None


class TaskQueryParams(TaskIdParams):
    pass


class TaskSendParams(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    sessionId: str = Field(default_factory=lambda: uuid.uuid4().hex)
    payload: dict
    acceptedOutputModes: Optional[List[str]] = None
    pushNotification: Optional[PushNotificationConfig] = None
    metadata: Optional[dict[str, Any]] = None


class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig


## RPC Messages


class JSONRPCMessage(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[int | str] = Field(default_factory=lambda: uuid.uuid4().hex)


class JSONRPCRequest(JSONRPCMessage):
    method: str
    params: Optional[dict[str, Any]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(JSONRPCMessage):
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None


class SendTaskRequest(JSONRPCRequest):
    method: Literal["tasks/send"] = "tasks/send"
    params: TaskSendParams


class SendTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class SendTaskStreamingRequest(JSONRPCRequest):
    method: Literal["tasks/sendSubscribe"] = "tasks/sendSubscribe"
    params: TaskSendParams


class SendTaskStreamingResponse(JSONRPCResponse):
    result: Optional[TaskStatusUpdateEvent | TaskArtifactUpdateEvent] = None


class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams


class GetTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class CancelTaskRequest(JSONRPCRequest):
    method: Literal["tasks/cancel",] = "tasks/cancel"
    params: TaskIdParams


class CancelTaskResponse(JSONRPCResponse):
    result: Optional[Task] = None


class SetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/set",] = "tasks/pushNotification/set"
    params: TaskPushNotificationConfig


class SetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class GetTaskPushNotificationRequest(JSONRPCRequest):
    method: Literal["tasks/pushNotification/get",] = "tasks/pushNotification/get"
    params: TaskIdParams


class GetTaskPushNotificationResponse(JSONRPCResponse):
    result: Optional[TaskPushNotificationConfig] = None


class TaskResubscriptionRequest(JSONRPCRequest):
    method: Literal["tasks/resubscribe",] = "tasks/resubscribe"
    params: TaskIdParams


TaskRequest = Union[
    SendTaskRequest,
    GetTaskRequest,
    CancelTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    TaskResubscriptionRequest,
    SendTaskStreamingRequest,
]
A2ARequest = TypeAdapter(
    Annotated[
        TaskRequest,
        Field(discriminator="method"),
    ]
)

## Error types


class JSONParseError(JSONRPCError):
    code: int = -32700
    message: str = "Invalid JSON payload"
    data: Optional[Any] = None


class InvalidRequestError(JSONRPCError):
    code: int = -32600
    message: str = "Request payload validation error"
    data: Optional[Any] = None


class MethodNotFoundError(JSONRPCError):
    code: int = -32601
    message: str = "Method not found"
    data: None = None


class InvalidParamsError(JSONRPCError):
    code: int = -32602
    message: str = "Invalid parameters"
    data: Optional[Any] = None


class InternalError(JSONRPCError):
    code: int = -32603
    message: str = "Internal error"
    data: Optional[Any] = None


class TaskNotFoundError(JSONRPCError):
    code: int = -32001
    message: str = "Task not found"
    data: None = None


class TaskNotCancelableError(JSONRPCError):
    code: int = -32002
    message: str = "Task cannot be canceled"
    data: None = None


class PushNotificationNotSupportedError(JSONRPCError):
    code: int = -32003
    message: str = "Push Notification is not supported"
    data: None = None


class UnsupportedOperationError(JSONRPCError):
    code: int = -32004
    message: str = "This operation is not supported"
    data: None = None


class ContentTypeNotSupportedError(JSONRPCError):
    code: int = -32005
    message: str = "Incompatible content types"
    data: None = None


class RPCTimeoutError(JSONRPCError):
    code: int = -32006
    message: str = "RPC call timed out"
    data: None = None


class RPCMethodNotFoundError(JSONRPCError):
    code: int = -32007
    message: str = "RPC method not found"
    data: None = None


class RPCExecutionError(JSONRPCError):
    code: int = -32008
    message: str = "RPC method execution failed"
    data: Optional[Any] = None


## RPC-specific request/response types

class RPCCallRequest(JSONRPCRequest):
    """RPC方法调用请求"""
    method: Literal["rpc/call"] = "rpc/call"
    params: dict[str, Any]  # 包含 target_agent_id, rpc_method, args, kwargs


class RPCCallResponse(JSONRPCResponse):
    """RPC方法调用响应"""
    result: Optional[Any] = None


def are_modalities_compatible(server_output_modes: List[str], client_output_modes: List[str]):
    """Modalities are compatible if they are both non-empty
    and there is at least one common element."""
    if client_output_modes is None or len(client_output_modes) == 0:
        return True

    if server_output_modes is None or len(server_output_modes) == 0:
        return True

    return any(x in server_output_modes for x in client_output_modes)


def append_metadata(metadata: dict[str, list], new_metadata: dict[str, Any]) -> None:
    """Append data to the metadata dictionary."""
    for key, value in new_metadata.items():
        if key not in metadata:
            metadata[key] = []
        if isinstance(value, list):
            metadata[key].extend(value)
        else:
            if not isinstance(metadata[key], list):
                metadata[key] = [metadata[key]]
            metadata[key].append(value)

def send_task_request(
    request_id: str,
    session_id: str,
    task_id: str,
    payload: dict[str, Any],
):
    return SendTaskRequest(
        id=request_id,
        params=TaskSendParams(
            id=task_id,
            sessionId=session_id,
            payload=payload,
        ),
    )