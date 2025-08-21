"""
Task Manager Module

This module provides abstract base class and concrete implementation for task management,
including task creation, status updates, notifications, and streaming responses.
"""

from abc import ABC, abstractmethod
import asyncio
import json
import os
import sys
import traceback
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sse_starlette.sse import EventSourceResponse
from typing_extensions import AsyncIterable, Union

from agentlin.core.types import *


class TaskManager(ABC):
    """
    Abstract base class for task management.

    Defines the interface for task operations including creation, retrieval,
    cancellation, and notification management.
    """

    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        """Cancel a task by ID."""
        pass

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Send/create a new task."""
        pass

    @abstractmethod
    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """Subscribe to task updates with streaming response."""
        pass

    @abstractmethod
    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        """Configure push notifications for a task."""
        pass

    @abstractmethod
    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        """Retrieve push notification configuration for a task."""
        pass

    @abstractmethod
    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[SendTaskResponse], JSONRPCResponse]:
        """Resubscribe to an existing task."""
        pass


class InMemoryTaskManager(TaskManager):
    """
    In-memory implementation of TaskManager.

    Stores tasks and related data in memory with thread-safe operations.
    Suitable for development and testing environments.
    """

    def __init__(self) -> None:
        """Initialize the in-memory task manager."""
        self.tasks: Dict[str, Task] = {}
        self.push_notification_infos: Dict[str, PushNotificationConfig] = {}
        self.task_sse_subscribers: Dict[str, List[asyncio.Queue]] = {}

        # Locks for thread safety
        self.lock = asyncio.Lock()
        self.subscriber_lock = asyncio.Lock()

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        """Retrieve a task by ID."""
        logger.info(f"Getting task {request.params.id}")
        task_query_params: TaskQueryParams = request.params

        async with self.lock:
            task = self.tasks.get(task_query_params.id)
            if task is None:
                logger.warning(f"Task {task_query_params.id} not found")
                return GetTaskResponse(id=request.id, error=TaskNotFoundError())

        return GetTaskResponse(id=request.id, result=task)

    async def on_cancel_task(self, request: CancelTaskRequest) -> CancelTaskResponse:
        """Cancel a task by ID."""
        logger.info(f"Cancelling task {request.params.id}")
        task_id_params: TaskIdParams = request.params

        async with self.lock:
            task = self.tasks.get(task_id_params.id)
            if task is None:
                logger.warning(f"Task {task_id_params.id} not found for cancellation")
                return CancelTaskResponse(id=request.id, error=TaskNotFoundError())

        # TODO: Implement actual task cancellation logic
        logger.warning(f"Task cancellation not implemented for {task_id_params.id}")
        return CancelTaskResponse(id=request.id, error=TaskNotCancelableError())

    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        pass

    @abstractmethod
    async def on_send_task_subscribe(self, request: SendTaskStreamingRequest) -> AsyncIterable[SendTaskStreamingResponse]:
        pass

    async def streaming_request(
        self,
        request_id: str,
        task_id: str,
        session_id: str,
        payload: dict,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendTaskStreamingRequest:
        return SendTaskStreamingRequest(
            id=request_id,
            params=TaskSendParams(
                id=task_id,
                sessionId=session_id,
                payload=payload,
                metadata=metadata,
            ),
        )


    async def invoke_request(
        self,
        request_id: str,
        task_id: str,
        session_id: str,
        payload: dict,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendTaskRequest:
        return SendTaskRequest(
            id=request_id,
            params=TaskSendParams(
                id=task_id,
                sessionId=session_id,
                payload=payload,
                metadata=metadata,
            ),
        )

    async def fail_streaming_response(self, request_id: str, task_id: str, error: JSONRPCError) -> SendTaskStreamingResponse:
        fail_task_status = TaskStatus(state=TaskState.FAILED, payload=error)
        await self.update_store(task_id, fail_task_status)
        return SendTaskStreamingResponse(
            id=request_id,
            result=TaskStatusUpdateEvent(
                id=task_id,
                status=fail_task_status,
                final=True,
                metadata={
                    "message_content": [{"type": "text", "text": error.message}],
                    "block_list": [],
                },
            ),
        )

    async def working_streaming_response(self, request_id: str, task_id: str, payload: Optional[Any] = None) -> SendTaskStreamingResponse:
        task_status = TaskStatus(state=TaskState.WORKING, payload=payload)
        await self.update_store(task_id, task_status)
        return SendTaskStreamingResponse(
            id=request_id,
            result=TaskStatusUpdateEvent(
                id=task_id,
                status=task_status,
                final=False,
            ),
        )

    async def complete_streaming_response(self, request_id: str, task_id: str, payload: Optional[Any] = None, metadata: Optional[dict] = None) -> SendTaskStreamingResponse:
        task_status = TaskStatus(state=TaskState.COMPLETED, payload=payload)
        await self.update_store(task_id, task_status)
        return SendTaskStreamingResponse(
            id=request_id,
            result=TaskStatusUpdateEvent(
                id=task_id,
                status=task_status,
                final=True,
                metadata=metadata,
            ),
        )

    async def tool_result_streaming_response(
        self,
        request_id: str,
        task_id: str,
        message_content: list[ContentData],
        block_list: list[Block],
        key: Optional[str] = None,
    ) -> SendTaskStreamingResponse:
        """Send a streaming response for tool results."""
        metadata = {
            "message_content": message_content,
            "block_list": block_list,
        }
        if key:
            metadata["key"] = key
        return SendTaskStreamingResponse(
            id=request_id,
            result=TaskArtifactUpdateEvent(
                id=task_id,
                metadata=metadata,
            ),
        )

    async def set_push_notification_info(self, task_id: str, notification_config: PushNotificationConfig) -> None:
        """Set push notification configuration for a task."""
        async with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                raise ValueError(f"Task not found for {task_id}")
            self.push_notification_infos[task_id] = notification_config

    async def get_push_notification_info(self, task_id: str) -> PushNotificationConfig:
        """Get push notification configuration for a task."""
        async with self.lock:
            task = self.tasks.get(task_id)
            if task is None:
                raise ValueError(f"Task not found for {task_id}")
            return self.push_notification_infos.get(task_id)

    async def has_push_notification_info(self, task_id: str) -> bool:
        """Check if push notification configuration exists for a task."""
        async with self.lock:
            return task_id in self.push_notification_infos

    async def on_set_task_push_notification(self, request: SetTaskPushNotificationRequest) -> SetTaskPushNotificationResponse:
        """Configure push notifications for a task."""
        logger.info(f"Setting task push notification {request.params.id}")
        task_notification_params: TaskPushNotificationConfig = request.params

        try:
            await self.set_push_notification_info(
                task_notification_params.id,
                task_notification_params.pushNotificationConfig,
            )
        except Exception as e:
            logger.error(f"Error while setting push notification info: {e}")
            return SetTaskPushNotificationResponse(
                id=request.id,
                error=InternalError(message="An error occurred while setting push notification info"),
            )

        return SetTaskPushNotificationResponse(
            id=request.id,
            result=task_notification_params,
        )

    async def on_get_task_push_notification(self, request: GetTaskPushNotificationRequest) -> GetTaskPushNotificationResponse:
        """Retrieve push notification configuration for a task."""
        logger.info(f"Getting task push notification {request.params.id}")
        task_params: TaskIdParams = request.params

        try:
            notification_info = await self.get_push_notification_info(task_params.id)
        except Exception as e:
            logger.error(f"Error while getting push notification info: {e}")
            return GetTaskPushNotificationResponse(
                id=request.id,
                error=InternalError(message="An error occurred while getting push notification info"),
            )

        return GetTaskPushNotificationResponse(
            id=request.id,
            result=TaskPushNotificationConfig(id=task_params.id, pushNotificationConfig=notification_info),
        )

    async def upsert_task(self, task_send_params: TaskSendParams) -> Task:
        """Create or update a task."""
        # logger.debug(f"Upserting task {task_send_params.id}")
        async with self.lock:
            task = self.tasks.get(task_send_params.id)
            if task is None:
                task = Task(
                    id=task_send_params.id,
                    sessionId=task_send_params.sessionId,
                    status=TaskStatus(state=TaskState.SUBMITTED),
                )
                self.tasks[task_send_params.id] = task
            return task

    async def on_resubscribe_to_task(self, request: TaskResubscriptionRequest) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        """Resubscribe to an existing task."""
        logger.info(f"Resubscription requested for task: {request}")
        return JSONRPCResponse(id=request.id, error=UnsupportedOperationError())

    async def update_store(self, task_id: str, status: TaskStatus, metadata: Optional[Dict] = None) -> Task:
        """Update task status and metadata in the store."""
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError:
                logger.error(f"Task {task_id} not found for updating")
                raise ValueError(f"Task {task_id} not found")

            task.status = status
            if metadata is not None:
                task.metadata = metadata
            return task

    async def setup_sse_consumer(self, task_id: str, is_resubscribe: bool = False) -> asyncio.Queue:
        """Set up a Server-Sent Events consumer for a task."""
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                if is_resubscribe:
                    raise ValueError("Task not found for resubscription")
                self.task_sse_subscribers[task_id] = []

            sse_event_queue = asyncio.Queue(maxsize=0)  # Unlimited queue size
            self.task_sse_subscribers[task_id].append(sse_event_queue)
            return sse_event_queue

    async def enqueue_events_for_sse(self, task_id: str, task_update_event: Any) -> None:
        """Enqueue events for all SSE subscribers of a task."""
        async with self.subscriber_lock:
            if task_id not in self.task_sse_subscribers:
                logger.debug(f"No SSE subscribers found for task {task_id}")
                return

            current_subscribers = self.task_sse_subscribers[task_id]
            for subscriber in current_subscribers:
                try:
                    await subscriber.put(task_update_event)
                except Exception as e:
                    logger.error(f"Failed to enqueue event for subscriber: {e}")

    async def dequeue_events_for_sse(self, request_id: str, task_id: str, sse_event_queue: asyncio.Queue) -> AsyncIterable[SendTaskStreamingResponse]:
        """Dequeue events for SSE streaming response."""
        try:
            while True:
                event = await sse_event_queue.get()

                if isinstance(event, JSONRPCError):
                    yield SendTaskStreamingResponse(id=request_id, error=event)
                    break

                yield SendTaskStreamingResponse(id=request_id, result=event)

                if isinstance(event, TaskStatusUpdateEvent) and event.final:
                    break
        except Exception as e:
            logger.error(f"Error in SSE event dequeue: {e}")
            yield SendTaskStreamingResponse(id=request_id, error=InternalError(message=f"SSE streaming error: {str(e)}"))
        finally:
            # Clean up subscriber when done
            async with self.subscriber_lock:
                if task_id in self.task_sse_subscribers:
                    try:
                        self.task_sse_subscribers[task_id].remove(sse_event_queue)
                    except ValueError:
                        logger.warning(f"SSE queue not found in subscribers for task {task_id}")


async def merge_streams(*streams: AsyncIterable) -> AsyncIterable[Any]:
    """
    Merge multiple asynchronous streams into a single stream.

    Args:
        *streams: Asynchronous streams to merge.

    Yields:
        Items from the merged streams.

    Example:
        async for item in merge_streams(stream1, stream2):
            process(item)
    """
    queue = asyncio.Queue()
    active_streams = len(streams)

    async def feed_queue(stream: AsyncIterable) -> None:
        """Feed items from a stream into the queue."""
        try:
            async for item in stream:
                await queue.put(item)
        except Exception as e:
            logger.error(f"Error in stream feeder: {e}")
        finally:
            await queue.put(None)  # Signal stream end

    # Start tasks for all streams
    tasks = [asyncio.create_task(feed_queue(stream)) for stream in streams]

    try:
        # Consume queue until all streams are done
        while active_streams > 0:
            item = await queue.get()
            if item is None:
                active_streams -= 1
                continue
            yield item
    finally:
        # Ensure all tasks are properly cleaned up
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _process_request(task_manager: TaskManager, request: Request) -> JSONResponse | EventSourceResponse:
    """
    Process incoming task management requests.

    Args:
        task_manager: The task manager instance to handle the request
        request: The incoming FastAPI request

    Returns:
        JSON response or Server-Sent Events response
    """
    logger.debug("Processing task management request")
    try:
        body = await request.json()
        json_rpc_request: TaskRequest = A2ARequest.validate_python(body)

        # Route request to appropriate handler
        handler_map = {
            GetTaskRequest: task_manager.on_get_task,
            SendTaskRequest: task_manager.on_send_task,
            SendTaskStreamingRequest: task_manager.on_send_task_subscribe,
            CancelTaskRequest: task_manager.on_cancel_task,
            SetTaskPushNotificationRequest: task_manager.on_set_task_push_notification,
            GetTaskPushNotificationRequest: task_manager.on_get_task_push_notification,
            TaskResubscriptionRequest: task_manager.on_resubscribe_to_task,
        }

        handler = handler_map.get(type(json_rpc_request))
        if handler is None:
            logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
            raise ValueError(f"Unexpected request type: {type(json_rpc_request)}")

        result = await handler(json_rpc_request)
        return _create_response(result)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return _handle_exception(e)


def _create_response(result: Any) -> JSONResponse | EventSourceResponse:
    """
    Create appropriate response based on result type.

    Args:
        result: The result from task manager operation

    Returns:
        JSON response for regular results, SSE response for async iterables
    """
    if isinstance(result, AsyncIterable):

        async def event_generator(result: AsyncIterable) -> AsyncIterable[Dict[str, str]]:
            """Generate SSE events from async iterable result."""
            async for item in result:
                yield {"data": item.model_dump_json(exclude_none=True)}

        return EventSourceResponse(event_generator(result))

    elif isinstance(result, JSONRPCResponse):
        return JSONResponse(result.model_dump(exclude_none=True))

    else:
        logger.error(f"Unexpected result type: {type(result)}")
        raise ValueError(f"Unexpected result type: {type(result)}")


def _handle_exception(e: Exception) -> JSONResponse:
    """
    Handle exceptions and create appropriate JSON-RPC error responses.

    Args:
        e: The exception to handle

    Returns:
        JSON response with appropriate error code and message
    """
    if isinstance(e, json.decoder.JSONDecodeError):
        json_rpc_error = JSONParseError()
    elif isinstance(e, ValidationError):
        json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
    else:
        logger.error(f"Unhandled exception: {e}")
        json_rpc_error = InternalError()

    response = JSONRPCResponse(id=None, error=json_rpc_error)
    return JSONResponse(response.model_dump(exclude_none=True), status_code=400)
