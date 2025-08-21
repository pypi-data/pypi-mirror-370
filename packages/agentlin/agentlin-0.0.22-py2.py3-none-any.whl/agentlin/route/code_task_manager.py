from typing_extensions import Union, AsyncIterable
import asyncio
import time
import os
import json
import uuid
import websockets

from agentlin.core.agent_schema import create_logger
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.types import *
from agentlin.tools.tool_code_interpreter import iopub_msg_to_tool_response, parse_msg_list_to_tool_response
from agentlin.code_interpreter.client import JupyterClient


class ExecuteRequest(BaseModel):
    kernel_id: str
    code: str  # Code to execute in Jupyter kernel
    mode: Literal["simple", "full", "debug"] = "full"  # Mode to return blocks, default is "full"

    # Optional parameters for Jupyter connection
    # If not provided, will use environment variables or default values
    timeout: int = 60  # seconds, default is 1 minutes
    jupyter_host: Optional[str] = None  # Jupyter host, default is None
    jupyter_port: Optional[str] = None  # Jupyter port, default is None
    jupyter_token: Optional[str] = None  # Jupyter token, default is None
    session_id: Optional[str] = None  # Optional session ID, if not provided a new one will be generated
    msg_id: Optional[str] = None  # Optional message ID, if not provided a new one will be generated
    username: Optional[str] = "user"  # Username for Jupyter connection, default is "user"

CODE_TASK_MANAGER = "code_task_manager"

class CodeTaskManager(InMemoryTaskManager):
    def __init__(
        self,
        agent_id: str,
        jupyter_host: str = os.getenv("JUPYTER_HOST", "localhost"),
        jupyter_port: int = os.getenv("JUPYTER_PORT", 8888),
        jupyter_token: str = os.getenv("JUPYTER_TOKEN", "jupyter_server_token"),
        jupyter_timeout: int = os.getenv("JUPYTER_TIMEOUT", 60),
        jupyter_username: str = os.getenv("JUPYTER_USERNAME", "user"),
    ):
        super().__init__()
        self.jupyter_host = jupyter_host
        self.jupyter_port = jupyter_port
        self.jupyter_token = jupyter_token
        self.jupyter_timeout = jupyter_timeout
        self.jupyter_username = jupyter_username
        self.client = JupyterClient(
            jupyter_host=jupyter_host,
            jupyter_port=jupyter_port,
            jupyter_token=jupyter_token,
        )

        # 初始化日志记录
        logger_id = f"{agent_id}/{CODE_TASK_MANAGER}"
        self.LOG_DIR = os.getenv("LOG_DIR", "output/logs")
        self.logger = create_logger(os.path.join(self.LOG_DIR, "agents"), logger_id)
        self.logger.info(f"初始化 {logger_id}: Jupyter host={jupyter_host}, port={jupyter_port}, token={jupyter_token}, timeout={jupyter_timeout}, username={jupyter_username}")

    def create_kernel(self) -> str:
        return self.client.create_kernel().get("id")

    def delete_kernel(self, kernel_id: str):
        return self.client.delete_kernel(kernel_id)

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        request_id = request.id
        task_id = task_send_params.id
        session_id = task_send_params.sessionId
        return self._stream_generator(request, session_id, request_id, task_id)

    async def _stream_generator(
        self,
        request: SendTaskStreamingRequest,
        session_id: str,
        request_id: str,
        task_id: str,
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            self.logger.error(f"Error in tool task: {req}")
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=req)
            yield resp
            return
        if not req.kernel_id:
            self.logger.error("kernel_id is required")
            error = JSONRPCError(code=-32000, message="kernel_id is required, but it is not provided or created failed")
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp
            return

        # 设置默认参数
        req.jupyter_host = req.jupyter_host or self.jupyter_host
        req.jupyter_port = req.jupyter_port or self.jupyter_port
        req.jupyter_token = req.jupyter_token or self.jupyter_token
        req.timeout = req.timeout or self.jupyter_timeout
        req.username = req.username or self.jupyter_username
        req.session_id = req.session_id or str(uuid.uuid4())
        req.msg_id = req.msg_id or str(uuid.uuid4())

        if not all([req.jupyter_host, req.jupyter_port, req.jupyter_token]):
            self.logger.error("Missing Jupyter connection config")
            error = JSONRPCError(code=-32000, message="Missing Jupyter connection config")
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp
            return

        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        url = f"ws://{req.jupyter_host}:{req.jupyter_port}/api/kernels/{req.kernel_id}/channels?token={req.jupyter_token}"

        # 构造 execute_request 消息
        request_msg = {
            "header": {
                "msg_id": req.msg_id,
                "username": req.username,
                "session": req.session_id,
                "msg_type": "execute_request",
                "version": "5.3",
            },
            "parent_header": {},
            "metadata": {},
            "content": {
                "code": req.code,
                "silent": False,
                "store_history": True,
                "user_expressions": {},
                "allow_stdin": False,
                "stop_on_error": True,
            },
        }
        start_time = time.time()
        self.logger.debug(f"Executing code in kernel {req.kernel_id} with timeout {req.timeout} seconds")

        async with websockets.connect(url, ping_interval=None) as ws:
            self.logger.debug(f"Connected to Jupyter kernel {req.kernel_id} at {url}")
            # 发送执行请求
            await ws.send(json.dumps(request_msg, ensure_ascii=False, separators=(",", ":")))

            # 接收执行结果
            while True:
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=1)
                except asyncio.TimeoutError:
                    # 判断是否超时
                    if time.time() - start_time > req.timeout:
                        self.logger.error("Execution timeout")
                        error = JSONRPCError(code=-32000, message=f"Execution timeout after {req.timeout} seconds. Starting at {start_time}, current time is {time.time()}")
                        resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
                        yield resp
                        return
                    continue

                iopub_msg: dict = json.loads(msg_raw)
                self.logger.debug(f"Received message: \n{json.dumps(iopub_msg, indent=2, ensure_ascii=False)}")

                # 只收集当前执行的消息
                if iopub_msg.get("parent_header", {}).get("msg_id") != req.msg_id:
                    continue

                # 处理 iopub 消息
                response = iopub_msg_to_tool_response(iopub_msg, req.mode)
                if response:
                    yield SendTaskStreamingResponse(
                        id=request_id,
                        result=TaskArtifactUpdateEvent(
                            id=task_id,
                            metadata=response,
                        ),
                    )

                self.logger.debug(f"Collected message: {req.msg_id}")

                if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                    self.logger.debug(f"Msg {req.msg_id} Execution completed, kernel is idle")
                    break

        resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

    def _validate_request(self, request: Union[SendTaskRequest, SendTaskStreamingRequest]):
        task_send_params: TaskSendParams = request.params
        try:
            req = ExecuteRequest.model_validate(task_send_params.payload)
        except Exception as e:
            self.logger.error(f"Invalid request payload: {e}")
            return InvalidParamsError(message=str(e))
        return req

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        req = self._validate_request(request)
        if isinstance(req, JSONRPCError):
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED, payload=req),
            )
            return SendTaskResponse(id=request.id, error=req)

        if not req.kernel_id:
            self.logger.error("kernel_id is required")
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED, payload="kernel_id is required, but it is not provided or created failed"),
            )
            return SendTaskResponse(
                id=request.id,
                error=JSONRPCError(code=-32000, message="kernel_id is required, but it is not provided or created failed"),
            )

        # 设置默认参数
        req.jupyter_host = req.jupyter_host or self.jupyter_host
        req.jupyter_port = req.jupyter_port or self.jupyter_port
        req.jupyter_token = req.jupyter_token or self.jupyter_token
        req.timeout = req.timeout or self.jupyter_timeout
        req.username = req.username or self.jupyter_username
        req.session_id = req.session_id or str(uuid.uuid4())
        req.msg_id = req.msg_id or str(uuid.uuid4())

        if not all([req.jupyter_host, req.jupyter_port, req.jupyter_token]):
            await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.FAILED, payload="Missing Jupyter connection config"),
            )
            return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message="Missing Jupyter connection config"))

        url = f"ws://{req.jupyter_host}:{req.jupyter_port}/api/kernels/{req.kernel_id}/channels?token={req.jupyter_token}"

        # 构造 execute_request 消息
        request_msg = {
            "header": {
                "msg_id": req.msg_id,
                "username": req.username,
                "session": req.session_id,
                "msg_type": "execute_request",
                "version": "5.3",
            },
            "parent_header": {},
            "metadata": {},
            "content": {
                "code": req.code,
                "silent": False,
                "store_history": True,
                "user_expressions": {},
                "allow_stdin": False,
                "stop_on_error": True,
            },
        }

        # 保存结果
        results = []

        start_time = time.time()
        self.logger.debug(f"Executing code in kernel {req.kernel_id} with timeout {req.timeout} seconds")

        async with websockets.connect(url, ping_interval=None) as ws:
            self.logger.debug(f"Connected to Jupyter kernel {req.kernel_id} at {url}")
            # 发送执行请求
            await ws.send(json.dumps(request_msg, ensure_ascii=False, separators=(",", ":")))

            # 接收执行结果
            while True:
                try:
                    msg_raw = await asyncio.wait_for(ws.recv(), timeout=1)
                except asyncio.TimeoutError:
                    # 判断是否超时
                    if time.time() - start_time > req.timeout:
                        self.logger.error("Execution timeout")
                        await self.update_store(
                            task_send_params.id,
                            TaskStatus(state=TaskState.FAILED, payload="Execution timeout"),
                        )
                        return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message="Execution timeout"))
                    continue

                iopub_msg: dict = json.loads(msg_raw)
                self.logger.debug(f"Received message: \n{json.dumps(iopub_msg, indent=2, ensure_ascii=False)}")

                # 只收集当前执行的消息
                if iopub_msg.get("parent_header", {}).get("msg_id") != req.msg_id:
                    continue

                # 处理 iopub 消息
                results.append(iopub_msg)

                self.logger.debug(f"Collected message: {req.msg_id}")

                if iopub_msg["msg_type"] == "status" and iopub_msg["content"].get("execution_state") == "idle":
                    self.logger.debug(f"Msg {req.msg_id} Execution completed, kernel is idle")
                    break
        result = parse_msg_list_to_tool_response(results, mode=req.mode)
        task = await self.update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            result,
        )
        return SendTaskResponse(id=request.id, result=task)
