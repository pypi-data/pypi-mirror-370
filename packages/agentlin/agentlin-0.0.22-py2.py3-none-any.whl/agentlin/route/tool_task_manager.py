import asyncio
import json
import os
import traceback
from typing import AsyncIterable
from typing_extensions import Any, AsyncGenerator
import uuid

from fastmcp import Client
from fastmcp.client.transports import ClientTransportT
from fastmcp.client.elicitation import ElicitRequestParams, ElicitResult, RequestContext, ClientSession, LifespanContextT

from loguru import logger

from agentlin.core.agent_message_queue import AgentMessageQueue
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.core.types import *
from agentlin.tools.builtin.file_system_tools import (
    ListDirectoryTool,
    ReadManyFilesTool,
    ReadFileTool,
    WriteFileTool,
    GlobTool,
    GrepTool,
    ReplaceInFileTool,
    BashTool,
    TodoWriteTool,
    TodoReadTool,
    MemoryTool,
)
from agentlin.tools.core import DiscoveredMcpTool


class CallToolRequest(BaseModel):
    call_name: str
    call_args: dict[str, Any]


TOOL_TASK_MANAGER = "tool_task_manager"


class ToolTaskManager(InMemoryTaskManager, AgentMessageQueue):
    def __init__(
        self,
        host_frontend_id: str,
        agent_id: str,
        mcp_config: ClientTransportT,
        target_directory: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
        *,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
        InMemoryTaskManager.__init__(self)
        AgentMessageQueue.__init__(
            self,
            agent_id=f"{agent_id}/{TOOL_TASK_MANAGER}",
            rabbitmq_host=rabbitmq_host,
            rabbitmq_port=rabbitmq_port,
            auto_ack=auto_ack,
            reconnect_initial_delay=reconnect_initial_delay,
            reconnect_max_delay=reconnect_max_delay,
            message_timeout=message_timeout,
            rpc_timeout=rpc_timeout,
        )
        self.host_frontend_id = host_frontend_id
        self.env = env
        self.client = Client(
            mcp_config,
            elicitation_handler=self.on_elicitation,
        )
        self.target_directory = target_directory
        self.name2tool: dict[str, BaseTool] = {}
        self.register_rpc_method("call_tool", self.call_tool)

    async def on_elicitation(
        self,
        message: str,
        response_type: type,
        params: ElicitRequestParams,
        context: RequestContext[ClientSession, LifespanContextT],
    ):
        # Present the message to the user and collect input
        # user_input = input(f"{message}: ")
        print(f"{message}")
        print("===Params===")
        print(params)
        print("===Context===")
        print(context)
        data = {
            "params": params.model_dump(),
        }
        result = await self.call_rpc(self.host_frontend_id, "elicitation", message, response_type, data, context)
        if not result:
            logger.error(f"Failed to send elicitation message to {self.host_frontend_id}")
            return ElicitResult(action="reject")

        return ElicitResult(action="accept", content=result)

    def apply_env_change(self, env: Optional[dict[str, str]]):
        if not env:
            return
        diff = {k: v for k, v in env.items() if k not in self.env or self.env[k] != v}
        if len(diff) == 0:
            return
        self.env.update(env)


    def get_function_declarations(self) -> List[FunctionDefinition]:
        return [tool.schema for tool in self.name2tool.values()]

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.name2tool.values())

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.name2tool.get(name)

    def register_tool(self, tool: BaseTool):
        if tool.name in self.name2tool:
            logger.warning(f'Warning: Tool "{tool.name}" already registered. Overwriting.')
        self.name2tool[tool.name] = tool

    async def discover_tools(self):
        tasks = [
            self.discover_mcp_tools(),
            self.discover_builtin_tools(self.target_directory)
        ]
        await asyncio.gather(*tasks)

    async def discover_mcp_tools(self):
        async with self.client:
            tools = await self.client.list_tools()
            for tool in tools:
                self.register_tool(DiscoveredMcpTool(self.client, tool))

    async def discover_builtin_tools(self, target_directory: Optional[str] = None):
        target_directory = target_directory if target_directory else os.getcwd()
        tools = [
            # ReadManyFilesTool(target_directory=target_directory),
            ListDirectoryTool(target_directory=target_directory),
            ReadFileTool(target_directory=target_directory),
            WriteFileTool(target_directory=target_directory),
            GlobTool(target_directory=target_directory),
            GrepTool(target_directory=target_directory),
            ReplaceInFileTool(target_directory=target_directory),
            BashTool(target_directory=target_directory),
            TodoWriteTool(target_directory=target_directory),
            TodoReadTool(target_directory=target_directory),
            MemoryTool(target_directory=target_directory),
        ]
        for tool in tools:
            self.register_tool(tool)

    async def get_tools(self, allowed_tools: Optional[list[str]] = None) -> list[ToolData]:
        if len(self.name2tool) == 0:
            await self.discover_builtin_tools(self.target_directory)
        results = []
        for name, tool in self.name2tool.items():
            if allowed_tools is None:
                results.append(tool.function_tool_schema)
                continue
            # 如果指定了 allowed_tools，则只返回这些工具
            if name in allowed_tools:
                results.append(tool.function_tool_schema)
        return results

    async def _handle_regular_message(self, msg: dict[str, Any]):
        """
        Handle regular (non-time) messages from other agents.

        Must be implemented by concrete agent classes to define
        agent-specific message handling behavior.

        Args:
            msg: The decoded message dictionary.
        """
        self.logger.info(msg)

    async def call_tool(
        self,
        request_id: str,
        call_id: str,
        session_id: str,
        call_name: str,
        call_args: dict[str, Any],
    ):
        tool_request = await self.invoke_request(
            request_id=request_id,
            task_id=call_id,
            session_id=session_id,
            payload={
                "call_name": call_name,
                "call_args": call_args,
            }
        )
        resp = await self.on_send_task(tool_request)
        return resp

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})
        return self._stream_generator(request.id, task_send_params.id, call_name, call_args)

    async def _stream_generator(
        self,
        request_id: str,
        task_id: str,
        call_name: str,
        call_args: dict[str, Any],
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        self.logger.debug(f"Tool Call\n{call_name}\n{call_args}")
        tool = self.get_tool(call_name)
        if not tool:
            error_message = f"Tool not found: {call_name}"
            self.logger.error(error_message)
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=JSONRPCError(code=-32000, message=error_message))
            yield resp
            return

        try:
            tool_result = await tool.execute(call_args)
            yield SendTaskStreamingResponse(
                id=request_id,
                result=TaskArtifactUpdateEvent(
                    id=task_id,
                    metadata=tool_result.model_dump(),
                ),
            )

        except Exception as e:
            error_message = f"Error while calling {call_name}: {e}"

            yield SendTaskStreamingResponse(
                id=request_id,
                result=TaskArtifactUpdateEvent(
                    id=task_id,
                    metadata={
                        "message_content": [{"type": "text", "text": error_message}],
                        "block_list": [],
                    },
                ),
            )
            self.logger.error(f"{error_message}\n{traceback.format_exc()}")
            error = JSONRPCError(code=-32000, message=error_message)
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        session_id = task_send_params.sessionId
        payload = task_send_params.payload
        call_id: str = payload.get("call_id", f"call_{uuid.uuid4().hex}")
        call_name: str = payload.get("call_name", "unknown_function")
        call_args: dict[str, Any] = payload.get("call_args", {})

        self.logger.debug(f"Tool Call\n{call_name}\n{call_args}")
        tool = self.get_tool(call_name)
        if not tool:
            error_message = f"Tool not found: {call_name}"
            self.logger.error(error_message)
            return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message=error_message))
        try:
            result = await tool.execute(call_args)
            self.logger.debug(f"Tool Result\n{result}")
            task = await self.update_store(
                task_send_params.id,
                TaskStatus(state=TaskState.COMPLETED),
                result,
            )
            return SendTaskResponse(id=request.id, result=task)
        except Exception as exc:
            self.logger.error(f"Error in tool task: {exc}")
            return SendTaskResponse(id=request.id, error=JSONRPCError(code=-32000, message=str(exc)))
