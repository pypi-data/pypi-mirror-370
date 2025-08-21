from fastmcp import Client
from typing_extensions import Any, AsyncIterable, Optional
import json
import traceback
import random

import httpx
from httpx_sse import connect_sse
from fastmcp.client.transports import ClientTransportT
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from agentlin.core.types import *
from agentlin.core.agent_message_queue import AgentMessageQueue


class AgentClient(AgentMessageQueue):
    def __init__(
        self,
        host_frontend_id: str,
        backend_url: str,
        *,
        mcp_config: Optional[ClientTransportT] = None,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
        AgentMessageQueue.__init__(
            self,
            agent_id=host_frontend_id,
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            auto_ack=auto_ack,
            reconnect_initial_delay=reconnect_initial_delay,
            reconnect_max_delay=reconnect_max_delay,
            message_timeout=message_timeout,
            rpc_timeout=rpc_timeout,
        )
        self.backend_url = backend_url
        self.register_rpc_method("elicitation", self.on_elicitation)
        self.client: Optional[Client] = None
        self.client_tools: Optional[list[ToolData]] = None
        if mcp_config:
            self.client = Client(mcp_config=mcp_config)

    async def initialize(self):
        if self.client and not self.client_tools:
            async with self.client:
                tools = await self.client.list_tools()
                tools = [{"type": "function", "function": tool.model_dump()} for tool in tools]
                self.client_tools = tools
        return await super().initialize()

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        user_input = input(f"{message}\n Please input (y/N): ")
        if user_input.strip().lower() in ["y", "yes"]:
            action = "accept"
        else:
            action = "reject"
        return ElicitResult(action=action)

    async def _handle_regular_message(self, message):
        self.logger.debug(f"Received regular message: {message}")

    async def chat(
        self,
        user_message_content: list[ContentData],
        host_frontend_id: str = "aime",
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: str = "123",
        host_agent_config: Optional[dict] = None,
        additional_allowed_tools: Optional[list[str]] = None,
        additional_tools: Optional[list] = None,
        instruction: Optional[str] = None,
        inference_args: Optional[dict[str, Any]] = None,
        cwd: Optional[str] = None,
    ):
        """
        发起对话聊天请求

        Args:
            user_message_content: 用户消息内容
            host_frontend_id: 前端 ID，默认为 "aime"
            trace_id: 跟踪 ID，如果为 None 则自动生成
            session_id: 会话 ID，如果为 None 则自动生成，通过控制 session_id 可以新启对话
            task_id: 任务 ID，如果为 None 则自动生成
            user_id: 用户 ID，默认为 "123"
            host_agent_config: 主机代理配置
            additional_allowed_tools: 额外允许的工具列表
            additional_tools: 额外的工具列表
            instruction: 用户指令
            inference_args: 推理参数，如 max_tokens
            cwd: 当前工作目录

        Returns:
            AsyncIterable[SendTaskStreamingResponse]: 流式响应
        """
        # 生成默认值
        if trace_id is None:
            trace_id = f"{random.randint(1000, 9999)}"
        if session_id is None:
            session_id = f"{random.randint(1000, 9999)}"  # 默认会话ID
        if task_id is None:
            task_id = f"{random.randint(1000, 9999)}"

        # 构建请求payload
        payload = {
            "trace_id": trace_id,
            "user_id": user_id,
            "host_frontend_id": host_frontend_id,
            "user_message_content": user_message_content,
            "key": host_frontend_id,
            "agent_config": host_agent_config,
            "additional_tools": additional_tools,
            "additional_allowed_tools": additional_allowed_tools,
            "instruction": instruction,
            "inference_args": inference_args or {},
            "cwd": cwd,
        }

        # 构建任务参数
        task_params = {
            "id": task_id,
            "sessionId": session_id,
            "payload": payload,
        }

        # 发送流式请求并返回结果
        stream = self.send_task_streaming(task_params)
        return stream

    async def show_streaming_response(self, stream: AsyncIterable[SendTaskStreamingResponse], task_id: str):
        """Process the streaming response from the task manager."""
        try:
            async for item in stream:
                if isinstance(item, SendTaskStreamingResponse):
                    if item.error:
                        self.logger.error(f"Error in task {task_id}: {item.error}")
                        continue
                    result = item.result
                    if result is None:
                        self.logger.warning(f"Received empty result for task {task_id}.")
                        continue
                    # result could be a TaskArtifactUpdateEvent or TaskStatusUpdateEvent
                    if isinstance(result, TaskArtifactUpdateEvent):
                        payload = result.metadata
                        self.logger.info(json.dumps(payload, ensure_ascii=False, indent=2))
                    elif isinstance(result, TaskStatusUpdateEvent):
                        final = result.final
                        if final:
                            self.logger.info(f"Task {task_id} completed with status: {result.status}")
                        else:
                            self.logger.info(f"Task {task_id} status updated: {result.status}")
                    else:
                        self.logger.debug(result)
                else:
                    self.logger.debug(f"Received unexpected item: {item}")
        except KeyboardInterrupt:
            self.logger.info("Streaming interrupted by user.")
        except Exception as e:
            self.logger.error(f"Error during streaming: {e}\n{traceback.format_exc()}")

    async def send_task_streaming(self, payload: dict[str, Any]) -> AsyncIterable[SendTaskStreamingResponse]:
        request = SendTaskStreamingRequest(params=payload)
        with httpx.Client(timeout=None) as client:
            with connect_sse(client, "POST", self.backend_url, json=request.model_dump()) as event_source:
                for sse in event_source.iter_sse():
                    yield SendTaskStreamingResponse(**json.loads(sse.data))

    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            print(f" -----> {self.backend_url}")
            response = await client.post(self.backend_url, json=request.model_dump(), timeout=60)
            response.raise_for_status()
            return response.json()

    async def send_task(self, payload: dict[str, Any]) -> SendTaskResponse:
        payload = TaskSendParams(**payload)
        request = SendTaskRequest(params=payload)
        return SendTaskResponse(**await self._send_request(request))

    async def get_task(self, payload: dict[str, Any]) -> GetTaskResponse:
        request = GetTaskRequest(params=payload)
        return GetTaskResponse(**await self._send_request(request))

    async def cancel_task(self, payload: dict[str, Any]) -> CancelTaskResponse:
        request = CancelTaskRequest(params=payload)
        return CancelTaskResponse(**await self._send_request(request))

    async def set_task_callback(self, payload: dict[str, Any]) -> SetTaskPushNotificationResponse:
        request = SetTaskPushNotificationRequest(params=payload)
        return SetTaskPushNotificationResponse(**await self._send_request(request))

    async def get_task_callback(self, payload: dict[str, Any]) -> GetTaskPushNotificationResponse:
        request = GetTaskPushNotificationRequest(params=payload)
        return GetTaskPushNotificationResponse(**await self._send_request(request))
