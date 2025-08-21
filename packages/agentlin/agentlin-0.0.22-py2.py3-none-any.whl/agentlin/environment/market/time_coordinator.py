import asyncio
import datetime
import json
import aio_pika
from agentlin.core.agent_message_queue import MSG_TIME_TICK, TIME_EXCHANGE_NAME, TIME_EXCHANGE_TYPE


class TimeCoordinator:
    """
    时间协调器 - 负责发送时间同步信号
    """

    def __init__(self, rabbitmq_host: str = "localhost", rabbitmq_port: int = 5672):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.connection = None
        self.channel = None
        self.time_exchange = None
        self.tick_id = 0
        self._shutdown = False

    async def connect(self):
        """连接到RabbitMQ"""
        self.connection = await aio_pika.connect_robust(host=self.rabbitmq_host, port=self.rabbitmq_port)
        self.channel = await self.connection.channel(publisher_confirms=True)

        self.time_exchange = await self.channel.declare_exchange(
            name=TIME_EXCHANGE_NAME,
            type=TIME_EXCHANGE_TYPE,
            durable=True,
        )

    async def start_time_coordination(self, interval: float = 2.0):
        """
        开始时间协调

        Args:
            interval: 时间间隔（秒），默认每2秒发送一次时间同步信号
        """
        while not self._shutdown:
            self.tick_id += 1
            current_time = datetime.datetime.now(datetime.timezone.utc)

            # 发送时间同步信号
            message_body = {"sender": "time_coordinator", "type": MSG_TIME_TICK, "payload": {"current_time": current_time.isoformat(), "tick_id": self.tick_id}}

            await self.time_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="trader.time_tick",
            )

            print(f"Sent TIME_TICK {self.tick_id} at {current_time}")
            await asyncio.sleep(interval)

    def stop(self):
        """停止时间协调"""
        self._shutdown = True

    async def close(self):
        """关闭连接"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
