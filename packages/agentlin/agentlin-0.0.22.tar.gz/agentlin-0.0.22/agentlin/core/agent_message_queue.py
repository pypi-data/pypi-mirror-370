"""
基于RabbitMQ的消息队列实现，提供多实例协调、时间同步和可扩展的消息通信能力。

实现原理：
1. 基于RabbitMQ的robust连接，支持自动重连和错误恢复
2. 支持实例间消息通信和时间同步机制
3. 类型安全的消息处理和结构化日志记录
4. 可扩展的消息处理架构，支持不同类型的实例实现
"""

import datetime
import json
import os
import sys
import time
import traceback
import uuid
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum

import aio_pika
from aio_pika import RobustConnection, RobustChannel, ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exceptions import AMQPConnectionError, AMQPChannelError
from loguru._logger import Logger, Core

from agentlin.core.agent_schema import create_logger
from agentlin.core.types import (
    TaskState,
    TaskStatus,
    Task,
    JSONRPCMessage,
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    RPCTimeoutError,
    RPCMethodNotFoundError,
    RPCExecutionError,
    RPCCallRequest,
    RPCCallResponse,
)


# 消息类型常量
MSG_STOP_AGENT = "STOP_AGENT"
MSG_TIME_TICK = "TIME_TICK"
MSG_AGENT_STATUS = "AGENT_STATUS"
MSG_TASK_REQUEST = "TASK_REQUEST"
MSG_TASK_RESPONSE = "TASK_RESPONSE"
MSG_RPC_REQUEST = "RPC_REQUEST"
MSG_RPC_RESPONSE = "RPC_RESPONSE"
MSG_RPC_ERROR = "RPC_ERROR"

# 交换机配置
AGENT_EXCHANGE_NAME = "agent_exchange"
AGENT_EXCHANGE_TYPE = ExchangeType.DIRECT
TIME_EXCHANGE_NAME = "time_exchange"
TIME_EXCHANGE_TYPE = ExchangeType.TOPIC
RPC_EXCHANGE_NAME = "rpc_exchange"
RPC_EXCHANGE_TYPE = ExchangeType.DIRECT


class MessageType(str, Enum):
    """消息类型枚举"""

    STOP_AGENT = "STOP_AGENT"
    TIME_TICK = "TIME_TICK"
    AGENT_STATUS = "AGENT_STATUS"
    TASK_REQUEST = "TASK_REQUEST"
    TASK_RESPONSE = "TASK_RESPONSE"
    RPC_REQUEST = "RPC_REQUEST"
    RPC_RESPONSE = "RPC_RESPONSE"
    REGULAR_MESSAGE = "REGULAR_MESSAGE"


@dataclass
class AgentMessage:
    """Agent消息数据结构"""

    sender: str
    recipient: Optional[str] = None
    message_type: str = MessageType.REGULAR_MESSAGE
    payload: Optional[Dict[str, Any]] = None
    timestamp: float = None
    message_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())


@dataclass
class TimeTickMessage:
    """时间同步消息数据结构"""

    current_time: str
    tick_id: Optional[int] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class AgentStatusMessage:
    """Agent状态消息数据结构"""

    agent_id: str
    status: TaskState
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class RPCRequest:
    """RPC请求数据结构"""

    request_id: str
    method_name: str
    args: list
    kwargs: dict
    timestamp: float
    reply_to: str  # 回复队列名称
    correlation_id: str  # 用于关联请求和响应

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class RPCResponse:
    """RPC响应数据结构"""

    request_id: str
    correlation_id: str
    success: bool
    result: Any = None
    error: str = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class RPCTimeoutException(Exception):
    """RPC调用超时异常"""

    pass


class RPCMethodError(Exception):
    """RPC方法调用错误异常"""

    pass


class MessageQueueError(Exception):
    """消息队列基础异常"""

    pass


class MessageQueueConnectionError(MessageQueueError):
    """连接异常"""

    pass


class AgentMessageError(MessageQueueError):
    """消息处理异常"""

    pass


def parse_datetime_utc(dt_str: str) -> Optional[datetime.datetime]:
    """
    Parse an ISO formatted datetime string and ensure the result is UTC offset-aware.
    If the input datetime string is offset-naive, it assumes UTC.
    """
    if not dt_str:
        return None
    dt = datetime.datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


class AgentMessageQueue(ABC):
    """
    基于RabbitMQ的消息队列，支持多实例协调、时间同步和RPC调用。

    提供以下功能：
    1. 实例间消息通信，支持点对点和广播通信
    2. 时间同步机制，确保多实例系统的一致性
    3. RPC远程过程调用，支持同步和异步调用
    4. 健壮的连接管理，支持自动重连和错误恢复
    5. 结构化日志和监控，便于调试和运维
    6. 可扩展的消息处理架构，支持自定义消息类型
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        rabbitmq_host: str = "localhost",
        rabbitmq_port: int = 5672,
        auto_ack: bool = False,
        reconnect_initial_delay: float = 5.0,
        reconnect_max_delay: float = 60.0,
        message_timeout: float = 30.0,
        rpc_timeout: float = 30.0,
    ):
        """
        初始化消息队列

        Args:
            agent_id: 唯一标识符，如果为None则自动生成UUID
            rabbitmq_host: RabbitMQ服务器主机名
            rabbitmq_port: RabbitMQ服务器端口
            auto_ack: 是否自动确认消息
            reconnect_initial_delay: 重连初始延迟时间（秒）
            reconnect_max_delay: 重连最大延迟时间（秒）
            message_timeout: 消息处理超时时间（秒）
            rpc_timeout: RPC调用默认超时时间（秒）
        """
        # 核心属性
        self.LOG_DIR = os.getenv("LOG_DIR", "output/logs")
        self.agent_id = agent_id if agent_id else str(uuid.uuid4())

        # 时间和状态管理
        self.current_time: Optional[datetime.datetime] = None
        self.current_tick_id: Optional[int] = None
        self.agent_status: TaskState = TaskState.UNKNOWN

        # RabbitMQ连接配置
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.auto_ack = auto_ack
        self.reconnect_initial_delay = reconnect_initial_delay
        self.reconnect_max_delay = reconnect_max_delay
        self.message_timeout = message_timeout
        self.rpc_timeout = rpc_timeout
        self.routing_key = f"agent.{self.agent_id}"

        # 连接状态管理
        self.connection: Optional[RobustConnection] = None
        self.channel: Optional[RobustChannel] = None

        # 通信组件
        self.agent_exchange: Optional[aio_pika.Exchange] = None
        self.agent_queue: Optional[aio_pika.Queue] = None
        self.agent_consumer_tag: Optional[str] = None

        # 时间同步组件
        self.time_exchange: Optional[aio_pika.Exchange] = None
        self.time_queue: Optional[aio_pika.Queue] = None
        self.time_consumer_tag: Optional[str] = None

        # RPC相关组件
        self.rpc_exchange: Optional[aio_pika.Exchange] = None
        self.rpc_queue: Optional[aio_pika.Queue] = None  # 接收RPC请求的队列
        self.reply_queue: Optional[aio_pika.Queue] = None  # 接收RPC响应的队列
        self.rpc_consumer_tag: Optional[str] = None
        self.reply_consumer_tag: Optional[str] = None
        self.registered_methods: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # 生命周期管理
        self._stop_event = asyncio.Event()
        self._shutdown = False
        self._message_handlers: Dict[str, Callable] = {}

        # 注册默认消息处理器
        self._register_default_handlers()

        # 初始化日志记录
        self.logger = create_logger(os.path.join(self.LOG_DIR, "agents"), self.agent_id)
        self.logger.info(f"初始化 {self.agent_id}，RabbitMQ主机: {self.rabbitmq_host}:{self.rabbitmq_port}")

    def _register_default_handlers(self):
        """注册默认消息处理器"""
        self._message_handlers[MessageType.STOP_AGENT] = self._handle_stop_agent
        self._message_handlers[MessageType.TIME_TICK] = self._handle_time_tick
        self._message_handlers[MessageType.AGENT_STATUS] = self._handle_agent_status
        self._message_handlers[MessageType.RPC_REQUEST] = self._handle_rpc_request
        self._message_handlers[MessageType.RPC_RESPONSE] = self._handle_rpc_response

    def register_message_handler(self, message_type: str, handler: Callable):
        """
        注册自定义消息处理器

        Args:
            message_type: 消息类型
            handler: 处理函数，接受message参数
        """
        self._message_handlers[message_type] = handler
        self.logger.info(f"注册消息处理器: {message_type}")

    async def connect(self):
        """
        建立到RabbitMQ的连接并设置交换机和队列

        实现指数退避策略进行健壮的连接管理，确保在分布式环境中的可靠运行。
        支持自动重连和错误恢复，对多实例协调研究至关重要。
        """
        delay = self.reconnect_initial_delay

        while not self._shutdown:
            try:
                self.logger.info(f"尝试连接到RabbitMQ: {self.rabbitmq_host}:{self.rabbitmq_port}")

                # 建立健壮连接，启用发布者确认
                self.connection = await aio_pika.connect_robust(host=self.rabbitmq_host, port=self.rabbitmq_port)
                self.channel = await self.connection.channel(publisher_confirms=True)
                await self.channel.set_qos(prefetch_count=1)

                # 设置实例间通信基础设施
                await self._setup_agent_infrastructure()

                # 设置时间同步基础设施
                await self._setup_time_infrastructure()

                # 设置RPC基础设施
                await self._setup_rpc_infrastructure()

                self.logger.info("成功连接到RabbitMQ并初始化基础设施")
                return

            except (AMQPConnectionError, AMQPChannelError) as e:
                self.logger.error(f"连接失败: {e}. {delay}秒后重试...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.reconnect_max_delay)
            except Exception as e:
                self.logger.error(f"连接设置时发生意外错误: {e}. {delay}秒后重试...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.reconnect_max_delay)

    async def _setup_agent_infrastructure(self):
        """设置Agent通信基础设施"""
        if not self.channel:
            raise MessageQueueConnectionError("Channel未初始化，无法设置Agent基础设施")

        # 声明Agent交换机
        self.agent_exchange = await self.channel.declare_exchange(
            name=AGENT_EXCHANGE_NAME,
            type=AGENT_EXCHANGE_TYPE,
            durable=True,
        )
        self.logger.debug(f"声明交换机 '{AGENT_EXCHANGE_NAME}' (类型: {AGENT_EXCHANGE_TYPE})")

        # 设置Agent专用队列（持久化，独占）
        self.agent_queue = await self.channel.declare_queue(
            name=self.routing_key,
            durable=True,
            exclusive=True,
        )
        self.logger.debug(f"声明独占队列 '{self.routing_key}'")

        # 绑定队列到交换机
        await self.agent_queue.bind(self.agent_exchange, routing_key=self.routing_key)
        self.logger.debug(f"绑定队列 '{self.routing_key}' 到交换机 '{AGENT_EXCHANGE_NAME}'")

    async def _setup_time_infrastructure(self):
        """设置时间同步基础设施"""
        if not self.channel:
            raise MessageQueueConnectionError("Channel未初始化，无法设置时间同步基础设施")

        # 声明时间同步交换机
        self.time_exchange = await self.channel.declare_exchange(
            name=TIME_EXCHANGE_NAME,
            type=TIME_EXCHANGE_TYPE,
            durable=True,
        )
        self.logger.debug(f"声明时间交换机 '{TIME_EXCHANGE_NAME}' (类型: {TIME_EXCHANGE_TYPE})")

        # 设置时间队列
        self.time_queue = await self.channel.declare_queue(
            name=f"time_queue.{self.agent_id}",
            durable=True,
            exclusive=True,
        )

        # 配置基于类型的路由键
        time_routing_key = self._get_time_routing_key()
        self.logger.info(f"时间路由键: {time_routing_key}")

        # 绑定时间队列到时间交换机
        await self.time_queue.bind(self.time_exchange, routing_key=time_routing_key)
        await self.time_queue.bind(self.time_exchange, routing_key="stop_agent")
        self.logger.info(f"{self.agent_id} 绑定到时间交换机 '{TIME_EXCHANGE_NAME}'")

    async def _setup_rpc_infrastructure(self):
        """设置RPC基础设施"""
        if not self.channel:
            raise MessageQueueConnectionError("Channel未初始化，无法设置RPC基础设施")

        # 声明RPC交换机
        self.rpc_exchange = await self.channel.declare_exchange(
            name=RPC_EXCHANGE_NAME,
            type=RPC_EXCHANGE_TYPE,
            durable=True,
        )
        self.logger.debug(f"声明RPC交换机 '{RPC_EXCHANGE_NAME}' (类型: {RPC_EXCHANGE_TYPE})")

        # 创建接收RPC请求的队列（持久化，非独占）
        self.rpc_queue = await self.channel.declare_queue(
            name=f"rpc_requests.{self.agent_id}",
            durable=True,
            exclusive=False,
        )

        # 绑定RPC请求队列到交换机
        await self.rpc_queue.bind(self.rpc_exchange, routing_key=f"rpc.{self.agent_id}")
        self.logger.debug(f"创建并绑定RPC请求队列 'rpc_requests.{self.agent_id}'")

        # 创建接收RPC响应的队列（临时的，独占的）
        self.reply_queue = await self.channel.declare_queue(
            name=f"rpc_replies.{self.agent_id}.{uuid.uuid4().hex[:8]}",
            durable=False,
            exclusive=True,
            auto_delete=True,
        )
        self.logger.debug(f"创建RPC回复队列 '{self.reply_queue.name}'")

    def _get_time_routing_key(self) -> str:
        """
        根据类型获取时间路由键

        Returns:
            适合该类型的路由键
        """
        if self.agent_id.startswith("candle") or self.agent_id.startswith("exchange"):
            return "data_source.#"
        else:
            return "agent.#"

    async def publish_time(self, msg_type: str, payload: dict, routing_key: str) -> None:
        """
        在时间交换机上发布消息

        用于环境中的时间协调消息。对于同步多Agent交互和维护
        确定性系统进展至关重要。

        Args:
            msg_type: 时间消息类型
            payload: 包含时间信息的消息载荷
            routing_key: 消息分发的路由键
        """
        if not self.time_exchange:
            self.logger.error("时间交换机未初始化，无法发布时间消息")
            return

        message = AgentMessage(
            sender=self.agent_id,
            message_type=msg_type,
            payload=payload,
        )

        try:
            await self.time_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(asdict(message)).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
            self.logger.debug(f"发布时间消息: {msg_type} -> {routing_key}")
        except Exception as e:
            self.logger.error(f"发布时间消息失败: {e}")
            raise AgentMessageError(f"Failed to publish time message: {e}")

    async def send_message(
        self,
        recipient_id: str,
        message_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        发送消息到Agent交换机

        启用多Agent协调研究的Agent间通信。
        recipient_id确定消息传递的路由键。

        Args:
            recipient_id: 接收者ID
            message_type: 消息类型
            payload: 消息载荷

        Returns:
            成功发送则返回True，否则返回False
        """
        if not self.agent_exchange:
            self.logger.error("交换机未初始化，无法发送消息")
            return False

        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient_id,
            message_type=message_type,
            payload=payload,
        )

        routing_key = f"agent.{recipient_id}"

        try:
            await self.agent_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(asdict(message)).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
            self.logger.debug(f"发送消息到 {recipient_id}: {message_type}")
            return True

        except (AMQPConnectionError, AMQPChannelError) as e:
            self.logger.error(f"发送消息到 '{recipient_id}' 失败: {e}. 尝试重新连接...")
            await self.reconnect()
            return False
        except Exception as e:
            self.logger.error(f"发送消息到 '{recipient_id}' 时发生意外错误: {e}")
            return False

    async def broadcast_message(
        self,
        message_type: str,
        payload: Optional[Dict[str, Any]] = None,
        target_pattern: str = "agent.*",
    ) -> bool:
        """
        广播消息到多个实例

        Args:
            message_type: 消息类型
            payload: 消息载荷
            target_pattern: 目标路由模式

        Returns:
            成功发送则返回True，否则返回False
        """
        if not self.agent_exchange:
            self.logger.error("交换机未初始化，无法广播消息")
            return False

        message = AgentMessage(
            sender=self.agent_id,
            message_type=message_type,
            payload=payload,
        )

        try:
            await self.agent_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(asdict(message)).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=target_pattern,
            )
            self.logger.debug(f"广播消息: {message_type} -> {target_pattern}")
            return True

        except Exception as e:
            self.logger.error(f"广播消息失败: {e}")
            return False

    async def send_status_update(self, status: TaskState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送状态更新

        Args:
            status: 状态
            metadata: 附加元数据

        Returns:
            成功发送则返回True，否则返回False
        """
        self.agent_status = status

        status_message = AgentStatusMessage(
            agent_id=self.agent_id,
            status=status,
            metadata=metadata,
        )

        return await self.broadcast_message(
            message_type=MessageType.AGENT_STATUS,
            payload=asdict(status_message),
        )

    def register_rpc_method(self, method_name: str, method: Callable):
        """
        注册RPC方法供其他实例调用

        Args:
            method_name: 方法名称
            method: 可调用对象（函数或方法）
        """
        self.registered_methods[method_name] = method
        self.logger.info(f"注册RPC方法: {method_name}")

    def register_rpc(self, method_name: Optional[str] = None):
        """
        装饰器：注册RPC方法

        Args:
            method_name: 可选的方法名称，如果不提供则使用函数名

        Example:
            @agent_queue.register_rpc("calculate")
            def calculate(x, y):
                return x + y

            @agent_queue.register_rpc()  # 使用函数名 "process_data"
            def process_data(data):
                return {"processed": data}
        """

        def decorator(func: Callable):
            name = method_name if method_name is not None else func.__name__
            self.register_rpc_method(name, func)
            return func

        return decorator

    async def call_rpc(
        self,
        target_agent_id: str,
        method_name: str,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Any:
        """
        异步调用其他实例的RPC方法

        Args:
            target_agent_id: 目标实例的ID
            method_name: 要调用的方法名
            *args: 位置参数
            timeout: 超时时间（秒），如果不指定则使用默认值
            **kwargs: 关键字参数

        Returns:
            方法的返回值

        Raises:
            RPCTimeoutException: 调用超时
            RPCMethodError: 调用出错
        """
        if timeout is None:
            timeout = self.rpc_timeout

        # 生成请求ID和关联ID
        request_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        # 创建RPC请求
        rpc_request = RPCRequest(
            request_id=request_id,
            method_name=method_name,
            args=list(args),
            kwargs=kwargs,
            timestamp=time.time(),
            reply_to=self.reply_queue.name,
            correlation_id=correlation_id,
        )

        # 创建Future用于等待响应
        future = asyncio.Future()
        self.pending_requests[correlation_id] = future

        try:
            # 发送RPC请求
            await self._send_rpc_request(target_agent_id, rpc_request)

            # 等待响应，带超时
            response = await asyncio.wait_for(future, timeout=timeout)

            if response.success:
                return response.result
            else:
                raise RPCMethodError(f"RPC call failed: {response.error}")

        except asyncio.TimeoutError:
            raise RPCTimeoutException(f"RPC call to {target_agent_id}.{method_name} timed out after {timeout} seconds")
        finally:
            # 清理挂起的请求
            self.pending_requests.pop(correlation_id, None)

    def call_rpc_sync(
        self,
        target_agent_id: str,
        method_name: str,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Any:
        """
        同步调用其他实例的RPC方法（阻塞式）

        这是call_rpc方法的同步版本，适用于同步代码环境。

        Args:
            target_agent_id: 目标实例的ID
            method_name: 要调用的方法名
            *args: 位置参数
            timeout: 超时时间（秒）
            **kwargs: 关键字参数

        Returns:
            方法的返回值
        """
        return asyncio.create_task(
            self.call_rpc(
                target_agent_id,
                method_name,
                *args,
                timeout=timeout,
                **kwargs,
            )
        ).result()

    async def consume(self):
        """
        开始异步消费消息

        启动常规通信和时间同步消息的消息消费。
        对系统环境中的多实例协调至关重要。
        """
        if not self.agent_queue:
            self.logger.error("队列未初始化，无法开始消费")
            return

        # 开始消费常规Agent消息
        self.agent_consumer_tag = await self.agent_queue.consume(self.on_message)
        self.logger.info("开始消费消息")

        if not self.time_queue:
            self.logger.error("时间队列未初始化，无法开始消费时间同步消息")
            return

        # 开始消费时间同步消息
        self.time_consumer_tag = await self.time_queue.consume(self.on_message)
        self.logger.info("开始消费时间同步消息")

        # 开始消费RPC消息
        await self._start_rpc_consumption()

    async def _start_rpc_consumption(self):
        """开始消费RPC消息"""
        if not self.rpc_queue or not self.reply_queue:
            self.logger.error("RPC队列未初始化，无法开始RPC消费")
            return

        # 开始消费RPC请求
        self.rpc_consumer_tag = await self.rpc_queue.consume(self.on_message)
        self.logger.info("开始消费RPC请求")

        # 开始消费RPC响应
        self.reply_consumer_tag = await self.reply_queue.consume(self.on_message)
        self.logger.info("开始消费RPC响应")

    async def on_message(self, message: AbstractIncomingMessage):
        """
        处理传入消息的回调函数

        处理常规通信和时间同步消息。
        实现适当的错误处理和消息确认，确保健壮的多实例协调。

        Args:
            message: 来自RabbitMQ的传入消息
        """
        async with message.process(ignore_processed=True):
            try:
                # 解析消息
                msg_data = json.loads(message.body.decode("utf-8"))

                # 尝试解析为AgentMessage结构
                try:
                    agent_message = AgentMessage(**msg_data)
                except TypeError:
                    # 兼容旧格式消息
                    msg_type = msg_data.get("type")
                    if msg_type:
                        agent_message = AgentMessage(
                            sender=msg_data.get("sender", "unknown"),
                            recipient=msg_data.get("recipient"),
                            message_type=msg_type,
                            payload=msg_data.get("payload", {}),
                        )
                    else:
                        self.logger.warning(f"无法解析消息格式: {msg_data}")
                        return

                # 处理消息
                await self._dispatch_message(agent_message)

            except json.JSONDecodeError as e:
                self.logger.error(f"JSON解码错误: {e}. 消息: {message.body}")
            except Exception as e:
                self.logger.error(f"处理消息时出错: {e}. 消息: {message.body}\n{traceback.format_exc()}")

    async def _dispatch_message(self, message: AgentMessage):
        """
        分发消息到对应的处理器

        Args:
            message: 解析后的消息
        """
        message_type = message.message_type

        # 查找消息处理器
        handler = self._message_handlers.get(message_type)

        if handler:
            try:
                # 调用处理器
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)

                self.logger.debug(f"处理消息: {message_type} (来自: {message.sender})")
            except Exception as e:
                self.logger.error(f"处理消息 {message_type} 时出错: {e}")
        else:
            # 交给抽象方法处理
            await self._handle_regular_message(message)

    async def _handle_stop_agent(self, message: AgentMessage):
        """处理停止消息"""
        self.logger.info(f"{self.agent_id} 收到停止信号，正在关闭")
        self.stop()

    async def _handle_time_tick(self, message: AgentMessage):
        """处理时间同步消息"""
        try:
            payload = message.payload or {}
            time_tick = TimeTickMessage(**payload)
            await self.handle_time_tick(time_tick)

            self.logger.debug(f"处理时间同步: {time_tick.current_time}")
        except Exception as e:
            self.logger.error(f"处理时间同步消息失败: {e}")

    async def _handle_agent_status(self, message: AgentMessage):
        """处理状态消息"""
        try:
            payload = message.payload or {}
            status_message = AgentStatusMessage(**payload)
            await self.handle_agent_status(status_message)

            self.logger.debug(f"处理状态: {status_message.agent_id} -> {status_message.status}")
        except Exception as e:
            self.logger.error(f"处理状态消息失败: {e}")

    async def _handle_rpc_request(self, message: AgentMessage):
        """处理收到的RPC请求"""
        try:
            payload = message.payload or {}
            rpc_request = RPCRequest(**payload)

            self.logger.debug(f"收到RPC请求: {rpc_request.method_name}")

            # 查找并执行方法
            response = await self._execute_rpc_method(rpc_request)

            # 发送响应
            await self._send_rpc_response(response, rpc_request.reply_to, rpc_request.correlation_id)

        except Exception as e:
            self.logger.error(f"处理RPC请求失败: {e}")
            # 发送错误响应
            try:
                payload = message.payload or {}
                error_response = RPCResponse(
                    request_id=payload.get("request_id", "unknown"),
                    correlation_id=payload.get("correlation_id", str(uuid.uuid4())),
                    success=False,
                    error=str(e),
                )
                reply_to = payload.get("reply_to")
                correlation_id = payload.get("correlation_id")
                if reply_to and correlation_id:
                    await self._send_rpc_response(error_response, reply_to, correlation_id)
            except Exception as send_error:
                self.logger.error(f"发送RPC错误响应失败: {send_error}")

    async def _handle_rpc_response(self, message: AgentMessage):
        """处理收到的RPC响应"""
        try:
            payload = message.payload or {}
            response = RPCResponse(**payload)

            # 找到对应的Future并设置结果
            correlation_id = response.correlation_id
            if correlation_id in self.pending_requests:
                future = self.pending_requests[correlation_id]
                if not future.done():
                    future.set_result(response)
                self.logger.debug(f"解析RPC响应，correlation_id: {correlation_id}")
            else:
                self.logger.warning(f"收到未知correlation_id的RPC响应: {correlation_id}")

        except Exception as e:
            self.logger.error(f"处理RPC响应失败: {e}")

    async def _send_rpc_request(self, target_agent_id: str, rpc_request: RPCRequest):
        """发送RPC请求到目标实例"""
        if not self.rpc_exchange:
            raise RPCMethodError("RPC exchange not initialized")

        message = AgentMessage(
            sender=self.agent_id,
            recipient=target_agent_id,
            message_type=MessageType.RPC_REQUEST,
            payload=asdict(rpc_request),
        )

        routing_key = f"rpc.{target_agent_id}"

        await self.rpc_exchange.publish(
            aio_pika.Message(
                body=json.dumps(asdict(message)).encode(),
                correlation_id=rpc_request.correlation_id,
                reply_to=rpc_request.reply_to,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )

        self.logger.debug(f"发送RPC请求到 {target_agent_id}.{rpc_request.method_name}")

    async def _execute_rpc_method(self, rpc_request: RPCRequest) -> RPCResponse:
        """执行RPC方法并返回响应"""
        method_name = rpc_request.method_name

        if method_name not in self.registered_methods:
            return RPCResponse(
                request_id=rpc_request.request_id,
                correlation_id=rpc_request.correlation_id,
                success=False,
                error=f"Method '{method_name}' not found",
            )

        try:
            method = self.registered_methods[method_name]

            # 执行方法（支持同步和异步方法）
            if asyncio.iscoroutinefunction(method):
                result = await method(*rpc_request.args, **rpc_request.kwargs)
            else:
                result = method(*rpc_request.args, **rpc_request.kwargs)

            return RPCResponse(
                request_id=rpc_request.request_id,
                correlation_id=rpc_request.correlation_id,
                success=True,
                result=result,
            )

        except Exception as e:
            self.logger.error(f"执行RPC方法 '{method_name}' 失败: {e}")
            return RPCResponse(
                request_id=rpc_request.request_id,
                correlation_id=rpc_request.correlation_id,
                success=False,
                error=str(e),
            )

    async def _send_rpc_response(self, response: RPCResponse, reply_to: str, correlation_id: str):
        """发送RPC响应"""
        if not self.channel:
            self.logger.error("Channel未初始化，无法发送RPC响应")
            return

        message = AgentMessage(
            sender=self.agent_id,
            recipient=None,
            message_type=MessageType.RPC_RESPONSE,
            payload=asdict(response),
        )

        # 直接发送到回复队列
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(asdict(message)).encode(),
                correlation_id=correlation_id,
                delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT,  # 响应消息不需要持久化
            ),
            routing_key=reply_to,
        )

        self.logger.debug(f"发送RPC响应，request_id: {response.request_id}")

    @abstractmethod
    async def _handle_regular_message(self, message: AgentMessage):
        """
        处理来自其他实例的常规（非系统）消息

        必须由具体的类实现，以定义特定的消息处理行为。

        Args:
            message: 解析后的消息
        """
        pass

    async def handle_time_tick(self, time_tick: TimeTickMessage):
        """
        处理时间同步事件

        更新当前时间和tick ID。对于在确定性系统模式下
        保持所有实例间一致的时间进展至关重要。

        Args:
            time_tick: 包含时间信息的消息
        """
        current_time_str = time_tick.current_time
        self.logger.debug(f"收到时间同步消息: {current_time_str}")

        try:
            current_time = parse_datetime_utc(current_time_str)
            if current_time is None:
                raise ValueError(f"无法解析时间字符串: {current_time_str}")

            self.current_time = current_time
            self.current_tick_id = time_tick.tick_id

        except Exception as e:
            self.logger.error(f"{self.agent_id} 收到无效的时间同步格式: {current_time_str}, 错误: {e}")

    async def handle_agent_status(self, status_message: AgentStatusMessage):
        """
        处理状态更新事件

        可以被子类重写以实现自定义的状态处理逻辑。

        Args:
            status_message: 状态消息
        """
        self.logger.info(f"收到状态更新: {status_message.agent_id} -> {status_message.status}")
        # 子类可以重写此方法以实现特定的状态处理逻辑

    async def reconnect(self):
        """
        使用指数退避尝试重新连接到RabbitMQ

        通过自动从连接故障中恢复来确保在分布式环境中的健壮运行。
        对长期运行的多实例系统至关重要。
        """
        self.logger.info("尝试重新连接到RabbitMQ...")
        try:
            await self.connect()
            await self.consume()
            self.logger.info("重新连接成功")
        except Exception as e:
            self.logger.error(f"重新连接失败: {e}")
            raise MessageQueueConnectionError(f"Reconnection failed: {e}")

    async def close(self):
        self.logger.info(f"开始关闭 {self.agent_id}")

        # 取消所有挂起的RPC请求
        for correlation_id, future in self.pending_requests.items():
            if not future.done():
                future.set_exception(RPCMethodError("Connection closed"))
        self.pending_requests.clear()

        # 直接关闭连接，让消费者自然停止
        if self.channel:
            try:
                if not self.channel.is_closed:
                    await self.channel.close()
                self.logger.info("通道已关闭")
            except Exception as e:
                self.logger.error(f"关闭通道失败: {e}")

        if self.connection and not self.connection.is_closed:
            try:
                await self.connection.close()
                self.logger.info("RabbitMQ连接已关闭")
            except Exception as e:
                self.logger.error(f"关闭RabbitMQ连接失败: {e}")

        self.logger.info(f"{self.agent_id} 已关闭")

    async def run(self):
        """
        主运行入口点

        开始消息消费并等待停止事件。
        确保关闭时的适当清理。
        """
        try:
            await self.consume()
            self.logger.info(f"{self.agent_id} 开始运行")
            await self._stop_event.wait()
        except Exception as e:
            self.logger.error(f"运行时出错: {e}")
            raise
        finally:
            await self.close()

    async def initialize(self):
        """
        在运行前初始化

        建立RabbitMQ连接并准备参与系统。
        """
        await self.connect()

        # 发送初始状态
        await self.send_status_update(TaskState.SUBMITTED)

        self.logger.info(f"{self.agent_id} 初始化完成")

    def stop(self):
        """
        发出停止运行的信号

        设置关闭标志并触发停止事件以进行优雅的终止。
        """
        self.logger.info(f"收到停止信号: {self.agent_id}")
        self._shutdown = True
        self._stop_event.set()

    # 向后兼容的方法
    async def process_time_tick(self, msg: Dict[str, Any]):
        """
        处理TIME_TICK消息以进行系统同步（向后兼容）

        委托给handle_time_tick方法进行特定的时间处理逻辑。

        Args:
            msg: TIME_TICK消息字典
        """
        payload = msg.get("payload", {})
        time_tick = TimeTickMessage(**payload)
        await self.handle_time_tick(time_tick)
