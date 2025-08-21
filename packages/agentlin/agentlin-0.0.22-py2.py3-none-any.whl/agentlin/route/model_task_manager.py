import copy
import os
import time
import traceback
from loguru import logger
from openai.types.chat.chat_completion import ChatCompletion
from typing_extensions import Any, AsyncGenerator, Union, AsyncIterable
import asyncio
import inspect
import json

import openai
from openai.types.responses import Response
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from openai.types.responses.response_output_item import (
    ResponseOutputMessage,
    ResponseFileSearchToolCall,
    ResponseFunctionToolCall,
    ResponseFunctionWebSearch,
    ResponseComputerToolCall,
    ResponseReasoningItem,
    ImageGenerationCall,
    ResponseCodeInterpreterToolCall,
    LocalShellCall,
    McpCall,
    McpListTools,
    McpApprovalRequest,
    ResponseOutputItem,
)
from openai.types.responses.response_stream_event import (
    ResponseStreamEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseCodeInterpreterCallCodeDeltaEvent,
    ResponseCodeInterpreterCallCodeDoneEvent,
    ResponseCodeInterpreterCallCompletedEvent,
    ResponseCodeInterpreterCallInProgressEvent,
    ResponseCodeInterpreterCallInterpretingEvent,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseErrorEvent,
    ResponseFileSearchCallCompletedEvent,
    ResponseFileSearchCallInProgressEvent,
    ResponseFileSearchCallSearchingEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseInProgressEvent,
    ResponseFailedEvent,
    ResponseIncompleteEvent,
    ResponseQueuedEvent,
    ResponseReasoningSummaryPartAddedEvent,
    ResponseReasoningSummaryPartDoneEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseReasoningTextDeltaEvent,
    ResponseReasoningTextDoneEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseRefusalDeltaEvent,
    ResponseRefusalDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseWebSearchCallCompletedEvent,
    ResponseWebSearchCallInProgressEvent,
    ResponseWebSearchCallSearchingEvent,
    ResponseImageGenCallCompletedEvent,
    ResponseImageGenCallGeneratingEvent,
    ResponseImageGenCallInProgressEvent,
    ResponseImageGenCallPartialImageEvent,
    ResponseMcpCallArgumentsDeltaEvent,
    ResponseMcpCallArgumentsDoneEvent,
    ResponseMcpCallCompletedEvent,
    ResponseMcpCallFailedEvent,
    ResponseMcpCallInProgressEvent,
    ResponseMcpListToolsCompletedEvent,
    ResponseMcpListToolsFailedEvent,
    ResponseMcpListToolsInProgressEvent,
    ResponseOutputTextAnnotationAddedEvent,
)
from agentlin.core.types import *
from agentlin.core.agent_schema import completion_messages_to_responses_messages, completion_tools_to_responses_tools, create_logger, remove_thoughts, remove_thoughts_in_messages
from agentlin.route.task_manager import InMemoryTaskManager
from agentlin.tools.validate import validate_function_call_arguments


MODEL_TASK_MANAGER = "model_task_manager"


class ModelTaskManager(InMemoryTaskManager):
    def __init__(
        self,
        agent_id: str,
    ):
        super().__init__()
        self.API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        self.BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not self.BASE_URL:
            raise ValueError("OPENAI_BASE_URL environment variable is not set.")
        self.client = openai.AsyncOpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)

        logger_id = f"{agent_id}/{MODEL_TASK_MANAGER}"
        self.LOG_DIR = os.getenv("LOG_DIR", "output/logs")
        self.logger = create_logger(os.path.join(self.LOG_DIR, "agents"), logger_id)
        self.logger.info(f"Initialized {logger_id} for agent {agent_id}")

        self.token_counter = 0
        self._total_reasoning_tokens = 0

    def track_tokens(self, tokens: int, message: str = "") -> None:
        """Track token usage for monitoring and recording."""
        self.token_counter += tokens
        self.logger.info(f"Received {tokens} tokens, new total {self.token_counter}")

        # Store the response content for reasoning context (avoid empty or JSON strings)
        if message and not message.startswith("{"):
            self._last_response_content = message
        self._last_reasoning_tokens = tokens
        self._total_reasoning_tokens += tokens

    def capture_reasoning_from_response(self, model: str, response: ChatCompletionChunk) -> None:
        """Helper method to capture reasoning tokens from OpenAI API response."""
        if hasattr(response, "usage") and hasattr(response.usage, "completion_tokens_details"):
            if hasattr(response.usage.completion_tokens_details, "reasoning_tokens"):
                self._last_reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
                self._total_reasoning_tokens += self._last_reasoning_tokens
                self.logger.debug(f"Captured {self._last_reasoning_tokens} reasoning tokens from {model} response")

    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        await self.upsert_task(request.params)
        task_send_params: TaskSendParams = request.params
        request_id = request.id
        task_id = task_send_params.id
        session_id = task_send_params.sessionId
        return self._stream_generator(request, session_id, request_id, task_id)

    async def _chat_completion_chunk_stream_from_completion_api(
        self,
        request_id: str,
        session_id: str,
        task_id: str,
        messages: list[DialogData],
        use_stream_backend: bool,
        inference_args: dict,
    ):
        if use_stream_backend:
            stream = await self.client.chat.completions.create(
                messages=messages,
                stream=True,
                **inference_args,
            )
            async for chunk in stream:
                self.capture_reasoning_from_response(chunk.model, chunk)
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )
        else:
            completion = await self.client.chat.completions.create(
                messages=messages,
                stream=False,
                **inference_args,
            )
            choice = completion.choices[0]
            message = choice.message
            content = message.content
            refusal = message.refusal
            tool_calls = message.tool_calls
            if content or refusal:
                chunk = ChatCompletionChunk(
                    id=f"{request_id}-0",
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                role=message.role,
                                content=content if content else None,
                                refusal=refusal if refusal else None,
                            ),
                            index=0,
                            finish_reason="stop",
                            logprobs=None,
                        )
                    ],

                    created=int(time.time()),
                    model=completion.model,
                    object="chat.completion.chunk",
                    service_tier=completion.service_tier,
                    # usage=response.usage,
                )
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )
            if tool_calls and len(tool_calls) > 0:
                # 处理函数调用输出
                delta_tool_calls = []
                for idx, tool_call in enumerate(tool_calls):
                    delta_tool_calls.append(ChoiceDeltaToolCall(
                        index=idx,
                        id=tool_call.id,
                        type=tool_call.type,
                        function=ChoiceDeltaToolCallFunction(
                            name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                        ),
                    ))
                chunk = ChatCompletionChunk(
                    id=completion.id,
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                role="assistant",
                                tool_calls=delta_tool_calls,
                            ),
                            index=0,
                            finish_reason="tool_calls",
                            logprobs=None,
                        )
                    ],
                    created=int(time.time()),
                    model=completion.model,
                    object="chat.completion.chunk",
                    service_tier=completion.service_tier,
                    # usage=response.usage,
                )
                self.capture_reasoning_from_response(chunk.model, chunk)
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )

    async def _chat_completion_chunk_stream_from_responses_api(
        self,
        request_id: str,
        session_id: str,
        task_id: str,
        messages: list[DialogData],
        use_stream_backend: bool,
        inference_args: dict,
    ):
        if "tools" in inference_args:
            tools = inference_args["tools"]
            inference_args["tools"] = completion_tools_to_responses_tools(tools)
        if "max_tokens" in inference_args:
            inference_args["max_output_tokens"] = int(inference_args["max_tokens"])
            del inference_args["max_tokens"]
        if "parallel_tool_calls" not in inference_args:
            # 默认开启并行工具调用
            inference_args["parallel_tool_calls"] = True
        force_selection_n = 1
        if "tool_choice" in inference_args and inference_args["tool_choice"] == "required":
            inference_args["tool_choice"] = "auto"
            force_selection_n = 10
        inference_args.update(
            {
                "store": False,
                # "store": True,
                "reasoning": {
                    "effort": "high",
                    "generate_summary": "detailed",
                    "summary": "auto",
                },
            }
        )
        model = inference_args["model"]
        name2tool = {tool["function"]["name"]: tool["function"] for tool in tools}

        messages: list[ResponsesDialogData] = completion_messages_to_responses_messages(messages, remove_thoughts=True)

        # self.logger.info(f"Session {session_id} messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        # self.logger.info(f"Session {session_id} inference_args: {json.dumps(inference_args, ensure_ascii=False, indent=2)}")

        if use_stream_backend:
            # 调用OpenAI流式API
            stream = await self.client.responses.create(
                input=messages,
                stream=True,
                timeout=1000,
                **inference_args,
            )
            # 处理流式响应
            tool_calls = []
            response: Optional[Response] = None
            async for event in stream:
                # self.logger.info(f"Received event: {event.model_dump_json(indent=2)}")
                if isinstance(event, ResponseCreatedEvent):
                    response = event.response
                elif isinstance(event, ResponseReasoningSummaryTextDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseReasoningSummaryTextDoneEvent):
                    print()
                elif isinstance(event, ResponseReasoningTextDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseReasoningTextDoneEvent):
                    print()
                elif isinstance(event, ResponseFunctionCallArgumentsDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseFunctionCallArgumentsDoneEvent):
                    print()
                elif isinstance(event, ResponseCodeInterpreterCallCodeDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseCodeInterpreterCallCodeDoneEvent):
                    print()
                elif isinstance(event, ResponseMcpCallArgumentsDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseMcpCallArgumentsDoneEvent):
                    print()
                elif isinstance(event, ResponseTextDeltaEvent):
                    print(event.delta, end="")
                elif isinstance(event, ResponseTextDoneEvent):
                    print()
                elif isinstance(event, ResponseOutputItemDoneEvent):
                    item: ResponseOutputItem = event.item
                    if isinstance(item, ResponseOutputMessage):
                        # 处理消息输出
                        content = ""
                        refusal = ""
                        for content_item in item.content:
                            if hasattr(content_item, "text"):
                                content += content_item.text
                            elif hasattr(content_item, "refusal"):
                                refusal += content_item.refusal
                        chunk = ChatCompletionChunk(
                            id=item.id,
                            choices=[
                                Choice(
                                    delta=ChoiceDelta(
                                        role=item.role,
                                        content=content if content else None,
                                        refusal=refusal if refusal else None,
                                    ),
                                    index=0,
                                    finish_reason="stop",
                                    logprobs=None,
                                )
                            ],
                            created=int(time.time()),
                            model=response.model if response else model,
                            object="chat.completion.chunk",
                            service_tier=response.service_tier if response else "auto",
                            # usage=response.usage,
                        )
                        self.capture_reasoning_from_response(chunk.model, chunk)
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            result=TaskArtifactUpdateEvent(
                                id=task_id,
                                metadata=chunk.model_dump(),
                            ),
                        )
                    elif isinstance(item, ResponseReasoningItem):
                        # 处理推理输出
                        content = ""
                        summary = ""
                        if item.encrypted_content:
                            content += item.encrypted_content
                        if item.summary:
                            for summary_item in item.summary:
                                summary += summary_item.text
                        final_content = content if content else summary
                        chunk = ChatCompletionChunk(
                            id=item.id,
                            choices=[
                                Choice(
                                    delta=ChoiceDelta(
                                        content=final_content,
                                        role="assistant",
                                    ),
                                    index=0,
                                    finish_reason=None,
                                    logprobs=None,
                                )
                            ],
                            created=int(time.time()),
                            model=response.model if response else model,
                            object="chat.completion.chunk",
                            service_tier=response.service_tier if response else "auto",
                            # usage=response.usage,
                        )
                        self.capture_reasoning_from_response(chunk.model, chunk)
                        metadata = chunk.model_dump()
                        metadata["choices"][0]["delta"]["reasoning_content"] = final_content
                        metadata["choices"][0]["delta"]["content"] = ""
                        yield SendTaskStreamingResponse(
                            id=request_id,
                            result=TaskArtifactUpdateEvent(
                                id=task_id,
                                metadata=metadata,
                            ),
                        )
                    elif isinstance(item, ResponseFunctionToolCall):
                        tool_calls.append(ChoiceDeltaToolCall(
                            index=len(tool_calls),
                            id=item.call_id,
                            type="function",
                            function=ChoiceDeltaToolCallFunction(
                                name=item.name,
                                arguments=item.arguments,
                            ),
                        ))
            if len(tool_calls) > 0:
                # 处理函数调用输出
                chunk = ChatCompletionChunk(
                    id=item.id,
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                role="assistant",
                                tool_calls=tool_calls,
                            ),
                            index=0,
                            finish_reason="tool_calls",
                            logprobs=None,
                        )
                    ],
                    created=int(time.time()),
                    model=response.model if response else model,
                    object="chat.completion.chunk",
                    service_tier=response.service_tier if response else "auto",
                    # usage=response.usage,
                )
                self.capture_reasoning_from_response(chunk.model, chunk)
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )

        else:
            response = None
            if force_selection_n == 1:
                response: Response = await self.client.responses.create(
                    input=messages,
                    stream=False,
                    **inference_args,
                )
            else:
                i = 0
                while i < force_selection_n:
                    i += 1
                    try:
                        response: Response = await self.client.responses.create(
                            input=messages,
                            stream=False,
                            **inference_args,
                        )
                    except Exception as e:
                        self.logger.error(f"({i}/{force_selection_n}) Error occurred: {e}\n{traceback.format_exc()}")
                        continue
                    if not response.output:
                        continue
                    found = False
                    for item in response.output:
                        # self.logger.debug(i)
                        # self.logger.debug(item)
                        if isinstance(item, ResponseFunctionToolCall):
                            # 验证 argument 的合法性
                            name = item.name
                            arguments = item.arguments
                            tool_definition = name2tool.get(name)
                            if not tool_definition:
                                continue
                            validated_arguments = validate_function_call_arguments(tool_definition["parameters"], arguments)
                            if not validated_arguments:
                                self.logger.warning(f"Function call arguments validation failed for {name}\n{arguments}")
                                continue
                            self.logger.success(f"Found tool call at {i} attempts, breaking loop")
                            found = True
                            break
                    if found:
                        break
            if not response:
                error_message = f"Response not found after {force_selection_n} attempts"
                self.logger.error(error_message)
                error = JSONRPCError(code=-32000, message=error_message)
                resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
                yield resp
                return

            output = response.output
            self.logger.warning(f"Response output: {json.dumps([o.model_dump() for o in output], ensure_ascii=False, indent=2)}")
            tool_calls = []
            for i, item in enumerate(output):
                if isinstance(item, ResponseOutputMessage):
                    # 处理消息输出
                    content = ""
                    refusal = ""
                    for content_item in item.content:
                        if hasattr(content_item, "text"):
                            content += content_item.text
                        elif hasattr(content_item, "refusal"):
                            refusal += content_item.refusal
                    chunk = ChatCompletionChunk(
                        id=item.id,
                        choices=[
                            Choice(
                                delta=ChoiceDelta(
                                    role=item.role,
                                    content=content if content else None,
                                    refusal=refusal if refusal else None,
                                ),
                                index=0,
                                finish_reason=None if i < len(output) - 1 else "stop",
                                logprobs=None,
                            )
                        ],
                        created=int(time.time()),
                        model=response.model,
                        object="chat.completion.chunk",
                        service_tier=response.service_tier,
                        # usage=response.usage,
                    )
                    self.capture_reasoning_from_response(chunk.model, chunk)
                    yield SendTaskStreamingResponse(
                        id=request_id,
                        result=TaskArtifactUpdateEvent(
                            id=task_id,
                            metadata=chunk.model_dump(),
                        ),
                    )
                elif isinstance(item, ResponseReasoningItem):
                    # 处理推理输出
                    content = ""
                    summary = ""
                    if item.encrypted_content:
                        content += item.encrypted_content
                    if item.summary:
                        for summary_item in item.summary:
                            summary += summary_item.text
                    final_content = content if content else summary
                    chunk = ChatCompletionChunk(
                        id=item.id,
                        choices=[
                            Choice(
                                delta=ChoiceDelta(
                                    content=final_content,
                                    role="assistant",
                                ),
                                index=0,
                                finish_reason=None,
                                logprobs=None,
                            )
                        ],
                        created=int(time.time()),
                        model=response.model,
                        object="chat.completion.chunk",
                        service_tier=response.service_tier,
                        # usage=response.usage,
                    )
                    self.capture_reasoning_from_response(chunk.model, chunk)
                    metadata = chunk.model_dump()
                    metadata["choices"][0]["delta"]["reasoning_content"] = final_content
                    metadata["choices"][0]["delta"]["content"] = ""
                    yield SendTaskStreamingResponse(
                        id=request_id,
                        result=TaskArtifactUpdateEvent(
                            id=task_id,
                            metadata=metadata,
                        ),
                    )
                elif isinstance(item, ResponseFunctionToolCall):
                    tool_calls.append(ChoiceDeltaToolCall(
                        index=len(tool_calls),
                        id=item.call_id,
                        type="function",
                        function=ChoiceDeltaToolCallFunction(
                            name=item.name,
                            arguments=item.arguments,
                        ),
                    ))
            if len(tool_calls) > 0:
                # 处理函数调用输出
                chunk = ChatCompletionChunk(
                    id=item.id,
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                role="assistant",
                                tool_calls=tool_calls,
                            ),
                            index=0,
                            finish_reason="tool_calls",
                            logprobs=None,
                        )
                    ],
                    created=int(time.time()),
                    model=response.model,
                    object="chat.completion.chunk",
                    service_tier=response.service_tier,
                    # usage=response.usage,
                )
                self.capture_reasoning_from_response(chunk.model, chunk)
                yield SendTaskStreamingResponse(
                    id=request_id,
                    result=TaskArtifactUpdateEvent(
                        id=task_id,
                        metadata=chunk.model_dump(),
                    ),
                )


    async def _stream_generator(
        self,
        request: SendTaskStreamingRequest,
        session_id: str,
        request_id: str,
        task_id: str,
    ) -> AsyncIterable[SendTaskStreamingResponse]:
        resp = await self.working_streaming_response(request_id=request_id, task_id=task_id)
        yield resp

        # 获取任务参数
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        messages: list[DialogData] = payload.get("messages", [])
        inference_args: dict = payload.get("inference_args", {})
        inference_args = copy.deepcopy(inference_args)
        use_responses_backend: bool = inference_args.pop("use_responses_backend", False)
        use_stream_backend: bool = inference_args.pop("use_stream_backend", False)

        args_to_remove = set(["debug"])
        for arg_name in args_to_remove:
            if arg_name in inference_args:
                inference_args.pop(arg_name)

        messages = remove_thoughts_in_messages(messages)
        if "tools" in inference_args:
            tools = inference_args["tools"]
            name2tool = {}
            for tool in tools:
                name = tool["function"]["name"]
                if name in name2tool:
                    self.logger.warning(f"发现工具名称存在重复: {name}\n{json.dumps(tool, ensure_ascii=False, indent=2)}\n以下工具已存在：\n{json.dumps(name2tool[name], ensure_ascii=False, indent=2)}")
                name2tool[name] = tool
            if len(name2tool) != len(tools):
                inference_args["tools"] = list(name2tool.values())

        try:
            if use_responses_backend:
                stream = self._chat_completion_chunk_stream_from_responses_api(
                    request_id=request_id,
                    session_id=session_id,
                    task_id=task_id,
                    messages=messages,
                    use_stream_backend=use_stream_backend,
                    inference_args=inference_args,
                )
            else:
                stream = self._chat_completion_chunk_stream_from_completion_api(
                    request_id=request_id,
                    session_id=session_id,
                    task_id=task_id,
                    messages=messages,
                    use_stream_backend=use_stream_backend,
                    inference_args=inference_args,
                )
            async for resp in stream:
                yield resp

            resp = await self.complete_streaming_response(request_id=request_id, task_id=task_id)
            yield resp

        except Exception as e:
            # 处理错误情况
            error_message = f"处理请求时发生错误: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_message)
            error = JSONRPCError(code=-32000, message=error_message)
            resp = await self.fail_streaming_response(request_id=request_id, task_id=task_id, error=error)
            yield resp

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        await self.upsert_task(request.params)
        return await self._invoke(request)

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        # 获取任务参数
        task_send_params: TaskSendParams = request.params
        payload = task_send_params.payload
        messages: list[DialogData] = payload.get("messages", [])
        inference_args: dict = payload.get("inference_args", {})

        response: ChatCompletion = await self.client.chat.completions.create(
            messages=messages,
            stream=False,
            **inference_args,
        )
        self.capture_reasoning_from_response(response.model, response)

        task = await self.update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            response,
        )
        return SendTaskResponse(id=request.id, result=task)


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    async def main():
        manager = ModelTaskManager(agent_id="test_agent")
        request = SendTaskStreamingRequest(
            id="test_request",
            params=TaskSendParams(
                id="test_task",
                sessionId="test_session",
                payload={
                    "messages": [
                        {
                            "role": "system",
                            "content": [
                                {
                                    "text": '你是问财, 基于同花顺旗下HithinkGPT的金融分析师，所有回答均基于同花顺专有数据与工具提供。\n\n你有两个命名空间，一个是用于工具调用的命名空间，另一个是用于代码执行的命名空间。我会用【工具】来描述工具调用的命名空间，用【函数】来描述代码解释器的命名空间。\n【工具】是注册为 functions 命名空间里的 tool_call 的工具。其中比较特别的是 CodeInterpreter 工具，它已经预先执行过一些代码(用 <code-interpreter> 标签包裹起来)，包含了丰富的函数和变量。\n【函数】是定义在 <code-interpreter> 标签中的函数。<code-interpreter> 标签内的代码是 *CodeInterpreter* 工具已经执行过的代码，其变量在之后的代码块中可以直接使用。\n你要把两个命名空间区分开，避免在 <code-interpreter> 标签中使用工具，也要避免在工具调用中使用函数。\n\n第一个代码块已经执行，其中预定义了丰富的函数，后续你可以调用这些函数获取信息：\n\n<code-interpreter>\nimport os\nfrom typing import Callable, Literal, Optional, TypedDict\nimport requests\nimport pandas as pd\nfrom agentlin.code_interpreter.jupyter_display import display_table\n\n# 以下函数实现均已经匿名化处理，URL 和 body json 均不是真实的\n# 所以你不允许直接使用 URL 发起请求，而只能使用封装好的函数\nURL = os.getenv("URL")\n\ndef FinScreener(query: str) -> Optional[pd.DataFrame]:\n    """\n\t使用自然语言筛选A股股票、美股、港股、基金、指数、宏观、可转债、期货、用户自选股等多个领域。输入必须明确资产类型、财务指标及目标值或图表形态；避免使用"看涨"或"趋势"等主观术语——仅使用量化标准；若需获取除筛选条件外的额外指标，请在条件后以冒号列出。返回的非空DataFrame将包含\'代码\'、\'名称\'、\'日期\'等固定列，以及根据查询条件和数据库生成的动态列。\n    Example:\n        ```python\n        df1 = FinScreener("市盈率低于15的股票")\n        df2 = FinScreener("自选股中出现双底形态且20日均线大于50日均线的股票​")\n        ```\n    """\n    req = requests.post(f"{URL}/finscreener", json={"query": query})\n    datas = req.json().get("datas", [])\n    if not datas:\n        return None\n    df = pd.DataFrame(datas)\n    print(df)\n    return df\n\ndef FinDatabase(domain: Literal[\'stock\', \'futures\', \'zhishu\', \'usstock\', \'hkstock\', \'fund\', \'fundcompany\', \'fundmanager\', \'macro\', \'insurance\', \'other\'], instrument: str, indicator: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:\n    """\n    获取A股股票、美股、港股、基金、指数、宏观、可转债、期货的行情及财务指标。指标包含行情数据、财务数据与图表形态。返回的非空DataFrame将包含\'代码\'、\'名称\'、\'日期\'等固定列，以及根据查询和数据库生成的动态列。\n    Example:\n        ```python\n        df1 = FinDatabase("stock", "同花顺", "macd", "20250115", "20250515")\n        df2 = FinDatabase("usstock", "AAPL", "股价", "20250115", "20250515")\n        df3 = FinDatabase("macro", "", "中国gdp", "20250115", "20250515")\n        ```\n    """\n    obj = {"domain": domain, "a": instrument, "b": indicator, "c": start_date, "d": end_date}\n    req = requests.post(f"{URL}/findatabase", json=obj)\n    datas = req.json().get("datas", [])\n    if not datas:\n        return None\n    df = pd.DataFrame(datas)\n    print(df)\n    return df\n\n\n</code-interpreter>\n\n当前代码环境已经转换为本地环境，你可以调用当前代码块中定义的所有函数。\n以上函数中，不提供返回值的函数会直接打印结果，你可以整理并抄写这些结果进行使用，而不是解析打印的字符串。\n\n\n## 功能 1: 数据分析思考\n1. 你可以使用 FinScreener, FinDatabase,获取数据，使用 Pandas DataFrame 来进行计算和分析。\n2. dataframe 变量在调用相应function后自动打印变量值，你不用再打印 dataframe 变量。\n3. FinDatabase 可以直接取到常用的技术指标数据，请优先考虑 FinDatabase 获取，最后再尝试使用价格数据计算。\n4. 计算技术指标时请考虑“指标启动期空白”，提前取足够老的数据（一般提前 60 天），以使最终计算出来的指标在指定时间区间内均有数据。\n5. WARNING: FinDatabase 和 FinScreener 返回的列名不固定，可能会有变化，所以你要分两步，第一步取数后先打印变量以查看列名，在下一步工具调用中再使用实际存在的列名。\n\n参考代码：\n<code-interpreter>\ndf_aapl = FinDatabase("stock","同花顺","收盘价","2025-05-15","2025-05-20")\ndf_ai = FinScreener("人工智能（AI）行业股票，且Guru评级 > 80；需包含Guru评级、市值、远期市盈率数据​")\n</code-interpreter>\n输出：\n```\n<FinDatabase>\nID: 838241\nQuery: Get Closing Price for Stock AAPL from 20250515 to 20250520\nSimilar Indicator Names: [\'Closing Price\']\nResult:\n4 results found:\n|code|Closing Price|date|name|\n|---|---|---|---|\n|AAPL.O|211.45|20250515|Apple|\n|AAPL.O|211.26|20250516|Apple|\n|AAPL.O|208.78|20250519|Apple|\n|AAPL.O|206.86|20250520|Apple|\n</FinDatabase>\n<FinScreener>\nID: 938024\nQuery: Stock in AI industry; Guru Rating, Market Cap, Forward P/E\nSimilar Indicator Names: [\'国际美股@Theme\', \'国际美股@Market Cap\', \'国际美股@Guru\', \'国际美股@Forward P/E\']\nResult:\nShowing first 1 rows of 524 results:\n524 results found:\n|stock code|stock name|Last Price|Last Change|Current Rating|Rating Date|Market Cap[20250723]|Trading Date|P/E(TTM)[20250723]|\n|---|---|---|---|---|---|---|---|---|---|---|\n|NVDA|Nvidia|$170.78|2.25%|Buy|20250425|$4167.03 billion|20250723|54.28|\n</FinScreener>\n```\n有些列名是 code 有些是 stock code，你需要根据实际情况来使用列名。看到标准化后的列名后，才可以进行数据分析和可视化：\n<code-interpreter>\nunique_codes = df_ai[\'stock code\'].unique()\nunique_codes\n</code-interpreter>\n\n\n## 功能 2: 可视化思考\n1. 你可以使用 plotly 来绘制图表。避免使用 fig.show() 或 plt.show()，而是直接返回 fig 图表对象。\n2. 你可以使用 FinDatabase 等函数来获取数据和进行预测。得到数据后你生成新的 dataframe 再用 plotly 绘图。\n注：在使用 plotly 绘制技术指标相关的图时，请截断缺少数据的时间区间，只保留有完整数据的时间区间用于绘图\n\n参考代码\n<code-interpreter>\nimport plotly.graph_objects as go\n\n# 首先整理数据，请检查是否所有展示周期中各个指标的数据已经获取完整，若有缺失请先调用工具来补充相关数据\ndates = ["2025-05-15", "2025-05-16", "2025-05-19", "2025-05-20"]\ndf = pd.DataFrame({\n    "TSLA": [342.82, 349.98, 342.09, 343.82],\n    "AAPL": [211.45, 211.26, 208.78, 206.86],\n}, index=pd.to_datetime(dates))\n\n# 绘制图表\nfig = go.Figure()\nfig.add_trace(go.Scatter(x=df.index, y=df["TSLA"], mode=\'lines\', name=\'TSLA\'))\nfig.add_trace(go.Scatter(x=df.index, y=df["AAPL"], mode=\'lines\', name=\'AAPL\'))\nfig.update_layout(title=\'TSLA vs AAPL\', xaxis_title=\'Date\', yaxis_title=\'Market Cap\') \n# 为适配移动端小屏显示，应尽量减小元素间距，并将图例设置为底部横向排列（过程省略）\nfig\n</code-interpreter>\n\n\n## 功能 3: 在回答中展示代码解释器中的可视化组件（如 fig）\n1. 你可以在 answer 中使用 apply 块来展示代码解释器中的可视化组件（如 fig）\n2. apply 块中仅包含变量名称而不是具体的变量值\n\n参考回答：\nOK, I have created the chart as following:\n<apply>\nfig\n</apply>\n\n\n## 功能 4: 工具和函数联动\n1. 你可以在工具调用后使用函数，也可以在函数调用后使用工具。\n\n参考过程：\n比如用户询问：画特斯拉 60 天股价，并把特朗普和马斯克吵架事件的节点画在图上\n首先你使用搜索工具 Search 查询相关事件，然后使用 FinDatabase 函数获取特斯拉的股价数据，接着使用 plotly 绘制图表，最后将事件节点添加到图表中。\n\n你会先用工具：\n{"arguments": "Trump and Musk feud","name": "Search"}\n\n然后用函数：\n<code-interpreter>\ndf = FinDatabase("Stock","TSLA","Closing Price","20250515","20250529")\ndf\n</code-interpreter>\n\n接着用 plotly 绘图：\n<code-interpreter>\nimport plotly.graph_objects as go\n\nfig = go.Figure()\n....# 使用 df 和 事件数据绘图\nfig\n</code-interpreter>\n\n最后回答：\nOK, here is the chart.\n<apply>\nfig\n</apply>\n\n## 你的回答需要遵循以下规则\n逻辑要求\n1.答复应以所提供的背景为基础，提供有见地、全面的分析，首先是明确的结论，然后是详细的解释，并表现出高度的金融和经济专业知识。\n2.主要关注直接针对用户当前查询的数据和信息。首选项请参考UserProfile，但避免基于UserProfile过度解释查询；保持个性化补充。\n3.根据用户的问题，在适当的情况下加入情感价值——例如，在市场波动期间提供保证，或赞扬用户提出了一个很好的问题。\n4.除非用户另有规定，或者如果输入包含在非美国市场上市的股票或资产，则默认假设查询与美国股票市场有关。\n\n格式要求\n1.用Markdown格式写答案，在合适的地方使用表格，并应用格式（例如粗体、副标题）来提高可读性。\n2.使用所提供数据中的信息时，以[^N]格式添加引用，其中N是对象的$ref值。引文应放在相关文本之后。不要在单独的部分或回复末尾包含任何其他引用或放置引用。\n3.添加一些表情符号，使回复更具吸引力和乐趣。\n\n任务执行原则\n1. 工具返回内容为最终执行结果，不会更新或追加新数据，请基于当前返回结果进行回答\n2. 你首先获取全面和多角度的背景信息，确保答案的深度与广度：使用 Search 工具获取资讯或分析并选取内容，使用AccessingFullText进行精读，使用 FinScreener、FinDatabase 函数来查询金融数据（查询失败时可尝试用Search工具兜底）\n3. 你结合获取到的信息使用 plotly 将数据可视化；可以将新闻事件、预测结果等一起加入到 plotly 图表中进行可视化\n4. 对于超出Knowledge Cutoff日期（Jun 01, 2024）或具有时效性的信息，应借助工具获取最新数据以确保准确性\n\n\n## 额外信息\n<User Profile>\n{{all_user_profile}}',
                                    "type": "text",
                                }
                            ],
                        },
                        {"role": "user", "content": [{"text": "分析下同花顺近一周股价和热点新闻", "type": "text"}]},
                    ],
                    "inference_args": {
                        "use_stream_backend": True,
                        "use_responses_backend": False,
                        # "model": "/mnt/model/gpt-oss-120b",
                        # "max_output_tokens": 1000,
                        # "background": False,
                        "max_tokens": 10 * 1024,
                        # "model": "/mnt/model/gpt-oss-120b",
                        "model": "/mnt/model/Qwen3-235B-A22B-Thinking-2507",
                        # "model": "o3",
                        # "parallel_tool_calls": True,
                        # "max_tool_calls": 5,
                        # "reasoning": {"effort": "high", "summary": "detailed"},
                        # "store": False,
                        # "stream": True,
                        "temperature": 1,
                        "tool_choice": "auto",
                        "tools": [
                            {
                                "function": {
                                    "name": "Search",
                                    "description": "A general search engine.",
                                    "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "query"}}, "required": ["query"]},
                                },
                                "type": "function",
                            },
                            {
                                "function": {
                                    "name": "CodeInterpreter",
                                    "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。你能看见之前已经执行的代码和执行结果，在生成新的代码时，请直接使用之前的变量名，而不是重新定义变量。",
                                    "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "要执行的 Python 代码。"}}, "required": ["code"]},
                                },
                                "type": "function",
                            },
                        ],
                        "top_p": 1,
                        # "truncation": "disabled",
                    },
                },
            ),
        )
        async for response in await manager.on_send_task_subscribe(request):
            logger.debug(response.result.metadata)

    asyncio.run(main())
    # import requests
    # import json

    # body = {
    #     "input": [
    #         {
    #             "role": "system",
    #             "content": [
    #                 {
    #                     "text": '你是问财, 基于同花顺旗下HithinkGPT的金融分析师，所有回答均基于同花顺专有数据与工具提供。\n\n你有两个命名空间，一个是用于工具调用的命名空间，另一个是用于代码执行的命名空间。我会用【工具】来描述工具调用的命名空间，用【函数】来描述代码解释器的命名空间。\n【工具】是注册为 functions 命名空间里的 tool_call 的工具。其中比较特别的是 CodeInterpreter 工具，它已经预先执行过一些代码(用 <code-interpreter> 标签包裹起来)，包含了丰富的函数和变量。\n【函数】是定义在 <code-interpreter> 标签中的函数。<code-interpreter> 标签内的代码是 *CodeInterpreter* 工具已经执行过的代码，其变量在之后的代码块中可以直接使用。\n你要把两个命名空间区分开，避免在 <code-interpreter> 标签中使用工具，也要避免在工具调用中使用函数。\n\n第一个代码块已经执行，其中预定义了丰富的函数，后续你可以调用这些函数获取信息：\n\n<code-interpreter>\nimport os\nfrom typing import Callable, Literal, Optional, TypedDict\nimport requests\nimport pandas as pd\nfrom agentlin.code_interpreter.jupyter_display import display_table\n\n# 以下函数实现均已经匿名化处理，URL 和 body json 均不是真实的\n# 所以你不允许直接使用 URL 发起请求，而只能使用封装好的函数\nURL = os.getenv("URL")\n\ndef FinScreener(query: str) -> Optional[pd.DataFrame]:\n    """\n\t使用自然语言筛选A股股票、美股、港股、基金、指数、宏观、可转债、期货、用户自选股等多个领域。输入必须明确资产类型、财务指标及目标值或图表形态；避免使用"看涨"或"趋势"等主观术语——仅使用量化标准；若需获取除筛选条件外的额外指标，请在条件后以冒号列出。返回的非空DataFrame将包含\'代码\'、\'名称\'、\'日期\'等固定列，以及根据查询条件和数据库生成的动态列。\n    Example:\n        ```python\n        df1 = FinScreener("市盈率低于15的股票")\n        df2 = FinScreener("自选股中出现双底形态且20日均线大于50日均线的股票​")\n        ```\n    """\n    req = requests.post(f"{URL}/finscreener", json={"query": query})\n    datas = req.json().get("datas", [])\n    if not datas:\n        return None\n    df = pd.DataFrame(datas)\n    print(df)\n    return df\n\ndef FinDatabase(domain: Literal[\'stock\', \'futures\', \'zhishu\', \'usstock\', \'hkstock\', \'fund\', \'fundcompany\', \'fundmanager\', \'macro\', \'insurance\', \'other\'], instrument: str, indicator: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:\n    """\n    获取A股股票、美股、港股、基金、指数、宏观、可转债、期货的行情及财务指标。指标包含行情数据、财务数据与图表形态。返回的非空DataFrame将包含\'代码\'、\'名称\'、\'日期\'等固定列，以及根据查询和数据库生成的动态列。\n    Example:\n        ```python\n        df1 = FinDatabase("stock", "同花顺", "macd", "20250115", "20250515")\n        df2 = FinDatabase("usstock", "AAPL", "股价", "20250115", "20250515")\n        df3 = FinDatabase("macro", "", "中国gdp", "20250115", "20250515")\n        ```\n    """\n    obj = {"domain": domain, "a": instrument, "b": indicator, "c": start_date, "d": end_date}\n    req = requests.post(f"{URL}/findatabase", json=obj)\n    datas = req.json().get("datas", [])\n    if not datas:\n        return None\n    df = pd.DataFrame(datas)\n    print(df)\n    return df\n\n\n</code-interpreter>\n\n当前代码环境已经转换为本地环境，你可以调用当前代码块中定义的所有函数。\n以上函数中，不提供返回值的函数会直接打印结果，你可以整理并抄写这些结果进行使用，而不是解析打印的字符串。\n\n\n## 功能 1: 数据分析思考\n1. 你可以使用 FinScreener, FinDatabase,获取数据，使用 Pandas DataFrame 来进行计算和分析。\n2. dataframe 变量在调用相应function后自动打印变量值，你不用再打印 dataframe 变量。\n3. FinDatabase 可以直接取到常用的技术指标数据，请优先考虑 FinDatabase 获取，最后再尝试使用价格数据计算。\n4. 计算技术指标时请考虑“指标启动期空白”，提前取足够老的数据（一般提前 60 天），以使最终计算出来的指标在指定时间区间内均有数据。\n5. WARNING: FinDatabase 和 FinScreener 返回的列名不固定，可能会有变化，所以你要分两步，第一步取数后先打印变量以查看列名，在下一步工具调用中再使用实际存在的列名。\n\n参考代码：\n<code-interpreter>\ndf_aapl = FinDatabase("stock","同花顺","收盘价","2025-05-15","2025-05-20")\ndf_ai = FinScreener("人工智能（AI）行业股票，且Guru评级 > 80；需包含Guru评级、市值、远期市盈率数据​")\n</code-interpreter>\n输出：\n```\n<FinDatabase>\nID: 838241\nQuery: Get Closing Price for Stock AAPL from 20250515 to 20250520\nSimilar Indicator Names: [\'Closing Price\']\nResult:\n4 results found:\n|code|Closing Price|date|name|\n|---|---|---|---|\n|AAPL.O|211.45|20250515|Apple|\n|AAPL.O|211.26|20250516|Apple|\n|AAPL.O|208.78|20250519|Apple|\n|AAPL.O|206.86|20250520|Apple|\n</FinDatabase>\n<FinScreener>\nID: 938024\nQuery: Stock in AI industry; Guru Rating, Market Cap, Forward P/E\nSimilar Indicator Names: [\'国际美股@Theme\', \'国际美股@Market Cap\', \'国际美股@Guru\', \'国际美股@Forward P/E\']\nResult:\nShowing first 1 rows of 524 results:\n524 results found:\n|stock code|stock name|Last Price|Last Change|Current Rating|Rating Date|Market Cap[20250723]|Trading Date|P/E(TTM)[20250723]|\n|---|---|---|---|---|---|---|---|---|---|---|\n|NVDA|Nvidia|$170.78|2.25%|Buy|20250425|$4167.03 billion|20250723|54.28|\n</FinScreener>\n```\n有些列名是 code 有些是 stock code，你需要根据实际情况来使用列名。看到标准化后的列名后，才可以进行数据分析和可视化：\n<code-interpreter>\nunique_codes = df_ai[\'stock code\'].unique()\nunique_codes\n</code-interpreter>\n\n\n## 功能 2: 可视化思考\n1. 你可以使用 plotly 来绘制图表。避免使用 fig.show() 或 plt.show()，而是直接返回 fig 图表对象。\n2. 你可以使用 FinDatabase 等函数来获取数据和进行预测。得到数据后你生成新的 dataframe 再用 plotly 绘图。\n注：在使用 plotly 绘制技术指标相关的图时，请截断缺少数据的时间区间，只保留有完整数据的时间区间用于绘图\n\n参考代码\n<code-interpreter>\nimport plotly.graph_objects as go\n\n# 首先整理数据，请检查是否所有展示周期中各个指标的数据已经获取完整，若有缺失请先调用工具来补充相关数据\ndates = ["2025-05-15", "2025-05-16", "2025-05-19", "2025-05-20"]\ndf = pd.DataFrame({\n    "TSLA": [342.82, 349.98, 342.09, 343.82],\n    "AAPL": [211.45, 211.26, 208.78, 206.86],\n}, index=pd.to_datetime(dates))\n\n# 绘制图表\nfig = go.Figure()\nfig.add_trace(go.Scatter(x=df.index, y=df["TSLA"], mode=\'lines\', name=\'TSLA\'))\nfig.add_trace(go.Scatter(x=df.index, y=df["AAPL"], mode=\'lines\', name=\'AAPL\'))\nfig.update_layout(title=\'TSLA vs AAPL\', xaxis_title=\'Date\', yaxis_title=\'Market Cap\') \n# 为适配移动端小屏显示，应尽量减小元素间距，并将图例设置为底部横向排列（过程省略）\nfig\n</code-interpreter>\n\n\n## 功能 3: 在回答中展示代码解释器中的可视化组件（如 fig）\n1. 你可以在 answer 中使用 apply 块来展示代码解释器中的可视化组件（如 fig）\n2. apply 块中仅包含变量名称而不是具体的变量值\n\n参考回答：\nOK, I have created the chart as following:\n<apply>\nfig\n</apply>\n\n\n## 功能 4: 工具和函数联动\n1. 你可以在工具调用后使用函数，也可以在函数调用后使用工具。\n\n参考过程：\n比如用户询问：画特斯拉 60 天股价，并把特朗普和马斯克吵架事件的节点画在图上\n首先你使用搜索工具 Search 查询相关事件，然后使用 FinDatabase 函数获取特斯拉的股价数据，接着使用 plotly 绘制图表，最后将事件节点添加到图表中。\n\n你会先用工具：\n{"arguments": "Trump and Musk feud","name": "Search"}\n\n然后用函数：\n<code-interpreter>\ndf = FinDatabase("Stock","TSLA","Closing Price","20250515","20250529")\ndf\n</code-interpreter>\n\n接着用 plotly 绘图：\n<code-interpreter>\nimport plotly.graph_objects as go\n\nfig = go.Figure()\n....# 使用 df 和 事件数据绘图\nfig\n</code-interpreter>\n\n最后回答：\nOK, here is the chart.\n<apply>\nfig\n</apply>\n\n## 你的回答需要遵循以下规则\n逻辑要求\n1.答复应以所提供的背景为基础，提供有见地、全面的分析，首先是明确的结论，然后是详细的解释，并表现出高度的金融和经济专业知识。\n2.主要关注直接针对用户当前查询的数据和信息。首选项请参考UserProfile，但避免基于UserProfile过度解释查询；保持个性化补充。\n3.根据用户的问题，在适当的情况下加入情感价值——例如，在市场波动期间提供保证，或赞扬用户提出了一个很好的问题。\n4.除非用户另有规定，或者如果输入包含在非美国市场上市的股票或资产，则默认假设查询与美国股票市场有关。\n\n格式要求\n1.用Markdown格式写答案，在合适的地方使用表格，并应用格式（例如粗体、副标题）来提高可读性。\n2.使用所提供数据中的信息时，以[^N]格式添加引用，其中N是对象的$ref值。引文应放在相关文本之后。不要在单独的部分或回复末尾包含任何其他引用或放置引用。\n3.添加一些表情符号，使回复更具吸引力和乐趣。\n\n任务执行原则\n1. 工具返回内容为最终执行结果，不会更新或追加新数据，请基于当前返回结果进行回答\n2. 你首先获取全面和多角度的背景信息，确保答案的深度与广度：使用 Search 工具获取资讯或分析并选取内容，使用AccessingFullText进行精读，使用 FinScreener、FinDatabase 函数来查询金融数据（查询失败时可尝试用Search工具兜底）\n3. 你结合获取到的信息使用 plotly 将数据可视化；可以将新闻事件、预测结果等一起加入到 plotly 图表中进行可视化\n4. 对于超出Knowledge Cutoff日期（Jun 01, 2024）或具有时效性的信息，应借助工具获取最新数据以确保准确性\n\n\n## 额外信息\n<User Profile>\n{{all_user_profile}}',
    #                     "type": "input_text",
    #                 }
    #             ],
    #             "type": "message",
    #         },
    #         {"role": "user", "content": [{"text": "分析下同花顺近一周股价和热点新闻", "type": "input_text"}], "type": "message"},
    #     ],
    #     "background": False,
    #     "max_output_tokens": 10240,
    #     "model": "/mnt/model/gpt-oss-120b",
    #     "parallel_tool_calls": True,
    #     "reasoning": {"effort": "high", "summary": "detailed"},
    #     "store": False,
    #     "stream": False,
    #     "temperature": 1,
    #     "tool_choice": "auto",
    #     "tools": [
    #         # {"type": "web_search"},
    #         {
    #             "name": "Search",
    #             "description": "A general search engine.",
    #             "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "query"}}, "required": ["query"]},
    #             "type": "function",
    #         },
    #         # {
    #         #     "name": "yu4ce4gong1ju4",
    #         #     "description": "预测工具，基于多维预测因子（市场数据、技术指标、行业趋势、基本面信息等）进行标的预测、诊断和智能推荐。可以预测股票/指数/行业板块/等标的未来表现；也可以依据预测结果进行不同维度的股票推荐。在调用时可以直接输入用户的问句，工具会自动根据用户的问句进行不同的内容规划。注意，在预测意图中，工具返回对应的预测结果以及在该预测结果的回测准确率。在推荐意图中，工具返回对应的推荐列表以及推荐的分数。",
    #         #     "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "开始"}}, "required": ["query"]},
    #         #     "type": "function",
    #         # },
    #         # {
    #         #     "name": "CodeInterpreter",
    #         #     "description": "在受限、安全的沙盒环境中执行 Python 3 代码的解释器，可用于数据处理、科学计算、自动化脚本、可视化等任务，支持大多数标准库及常见第三方科学计算库。你能看见之前已经执行的代码和执行结果，在生成新的代码时，请直接使用之前的变量名，而不是重新定义变量。",
    #         #     "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "要执行的 Python 代码。"}}, "required": ["code"]},
    #         #     "type": "function",
    #         # },
    #     ],
    #     "top_p": 1,
    #     "truncation": "disabled",
    # }
    # # body = {
    # #     "input": "You are a planning agent named Aime created by Ainvest Fintech, Inc., and your responsibility is to plan the use of tools to help me acquire sufficient background knowledge so that I can answer user questions well. You have permission to use the following tools:\n\nFinQuery: Retrieve specific indicators for selected stocks and options, or screen them based on defined criteria, with support for querying multiple indicators across multiple assets\nETFQuery: Retrieve specific indicators for selected ETFs or screen ETFs meeting defined criteria, with support for querying multiple indicators across multiple ETFs.\nIndexQuery: Retrieve specific indicators for selected indices or GICS classifications (industries, sectors, groups), or screen them based on defined criteria, with support for querying multiple indicators across multiple targets.\nSearch: This is a general search engine.\nStockNews: Use this tool when you want to get the latest information on stocks, indexes, concepts, commodities, and other subjects. Its input is usually a subject.\nClarify: Use this tool when you think the question is unclear or violates common sense. You can call this tool to ask the user for more information or provide the user with a second confirmation.\nCalculator: An advanced calculator that solves complex mathematical problems, input takes natural language and must include all necessary data for problem resolution.\nAccountQuery: Supports retrieving user’s trading portfolio data and optimizing it based on return metrics or specified stocks.\nBackTest: Use this tool when strategy backtesting or event backtesting is required. The tool accepts input in the form of natural language, and its output is a comprehensive backtesting report corresponding to the strategy or event backtested.\nMacroQuery: Obtain macroeconomics data such as GDP, M1, Unemployment Rate, National Debt, and population.\nForecast: Provide forecast on stocks, select the most suitable forecasting materials and return the corresponding results\nReminder: Set a reminder task based on natural language input, which must include the reminder content and at least one of the following: frequency, date, or time.\nCryptoQuery: Retrieve specific indicators for selected cryptocurrencies, or screen them based on defined criteria, covering cryptocurrency-specific indices such as Fear & Greed Index and ahr999; input should always specify domain \"Crypto\" and default to USD pairs unless specified, with support for querying multiple indicators across multiple assets.\n\nUse the following format:\nQuestion: A question you must answer.\nThought: You must always think about how to act.\nActionList: A list of actions that need to be executed at a certain stage, each action consists of tool name and tool input. where the tool name is one of the following: FinQuery,ETFQuery,IndexQuery,Search,StockNews,Clarify,Calculator,AccountQuery,BackTest,MacroQuery,Forecast,Reminder,CryptoQuery, and the input to the tool is all or part of the problem. The action list has multiple lines, and each line is represented by tool name: tool input. It is great important that actions that do not depend on each other must be executed in the same stage.\nObservation: The fusion result after all executions of the action list.\n... (such Thought/ActionList/Observation can be repeated N times)\nThought: The information is complete and I know how to answer.\n<FINISHED>\n\nYou must comply with the following principles:\n1. The most important thing is that your thinking and actions must be deep and comprehensive, maintaining your ability to associate and innovate, which largely determines whether I can have enough information to answer this question in the end.\n2. In the first thought, you should understand the user's question and devise a global plan in an inductive manner.\n3. Every subsequent thought should be based on current observations and an objective judgment on whether to continue the plan or revise it.\n4. You don't need to give the final answer.  If you think the information you observed is enough to answer the question, you only need to give a final tag \"<FINISHED>\".\n5. When you feel that you do not need any additional information to answer this question, you can directly enter the answer stage without performing any actions.\n6. The input of Clarify tool must be consistent with the language of the user's question.\n7. Except for the Clarify tool, the input of other tools and your Thought must be in English.\n\nBegin!\n\n<context>\nIf you think that these contextual information will help you answer and think, please refer to them:\nNLU:\n|code|name|type|benchmark|\n|---|---|---|---|\n|SPY.P|SPDR S&P 500 ETF Trust|etf_fund|S&P 500 Index|\n\nTIME:\nThursday, 2025-08-07 08:53:20\n</context>\n\n<user_profile>\nRefer to this when the user requests to use their preferences or profile; if clarification is necessary, review this information first:\nThe user has shown a keen interest in the NASDAQ Composite Index, indicating a preference for a diversified investment approach. Over the last two months, the user has clicked on the index once, suggesting a focus on market sentiment and potentially a news-driven strategy. This behavior could indicate a moderate to high risk tolerance, as the user is actively engaging with the market. The user's investment horizon appears to be relatively short-term, as evidenced by the recent clicks on the index.\n</user_profile>\n\n<history>\nIf the user's questions are related to the questions and answers in the conversation history, you need to consider them comprehensively before thinking and taking action:\n\n</history>\n\nQuestion: Is the SPY ETF bullish?\n\nThought:",
    # #     "model": "/mnt/model/gpt-oss-120b",
    # #     "stream": False,
    # #     # "top_p": 1,
    # #     # "truncation": "disabled",
    # #     # "background": False,
    # #     # "max_output_tokens": 10240,
    # #     # "parallel_tool_calls": True,
    # #     "reasoning": {"effort": "high", "summary": "detailed"},
    # #     # "store": False,
    # #     # "stream": False,
    # #     # "temperature": 1,
    # # }
    # # body = json.loads(text)
    # # print(json.dumps(body, indent=2, ensure_ascii=False))
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "Bearer aime_gpt_oss",
    # }
    # url = "http://10.217.219.2:2408/v1/responses"
    # # url = "http://10.244.247.236:8120/v1/responses"
    # response = requests.post(url, headers=headers, json=body)
    # print(response)
    # print(response.text)

    # # from httpx_sse import connect_sse
    # # import httpx

    # # with httpx.Client(timeout=None, headers=headers) as client:
    # #     with connect_sse(client, "POST", url, json=body) as event_source:
    # #         for sse in event_source.iter_sse():
    # #             print(json.loads(sse.data))
