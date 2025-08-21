
import asyncio
import datetime
import json
import random
from typing import Dict, Any

from agentlin.core.agent_message_queue import AgentMessageQueue, AgentMessage


class TradingAgent(AgentMessageQueue):
    """
    交易代理示例实现

    这个代理可以:
    - 接收和发送交易相关消息
    - 处理时间同步
    - 管理交易状态
    """

    def __init__(self, agent_id: str = None, **kwargs):
        super().__init__(agent_id=agent_id, **kwargs)
        self.portfolio = {"cash": 10000.0, "positions": {}}
        self.trade_count = 0

    async def _handle_regular_message(self, msg: AgentMessage):
        """处理来自其他代理的常规消息"""
        sender = msg.sender
        message_type = msg.message_type
        payload = msg.payload or {}

        self.logger.info(f"Received message from {sender}: {message_type}")

        if message_type == "TRADE_REQUEST":
            await self._handle_trade_request(sender, payload)
        elif message_type == "MARKET_DATA":
            await self._handle_market_data(sender, payload)
        elif message_type == "GREETING":
            await self._handle_greeting(sender, payload)
        else:
            self.logger.warning(f"Unknown message type: {message_type}")

    async def _handle_trade_request(self, sender: str, payload: Dict[str, Any]):
        """处理交易请求"""
        symbol = payload.get("symbol")
        quantity = payload.get("quantity", 0)
        price = payload.get("price", 0.0)

        self.logger.info(f"Processing trade request: {symbol} x {quantity} @ {price}")

        # 模拟交易逻辑
        if self.portfolio["cash"] >= quantity * price:
            # 执行买入
            self.portfolio["cash"] -= quantity * price
            self.portfolio["positions"][symbol] = (
                self.portfolio["positions"].get(symbol, 0) + quantity
            )
            self.trade_count += 1

            # 发送交易确认
            await self.send_message(
                sender,
                "TRADE_CONFIRMATION",
                {
                    "trade_id": self.trade_count,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "status": "EXECUTED"
                }
            )
            self.logger.info(f"Trade executed: {symbol} x {quantity} @ {price}")
        else:
            # 发送拒绝消息
            await self.send_message(
                sender,
                "TRADE_REJECTION",
                {
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "reason": "Insufficient funds"
                }
            )
            self.logger.warning(f"Trade rejected: Insufficient funds")

    async def _handle_market_data(self, sender: str, payload: Dict[str, Any]):
        """处理市场数据"""
        symbol = payload.get("symbol")
        price = payload.get("price")
        volume = payload.get("volume")

        self.logger.info(f"Market data: {symbol} = ${price} (volume: {volume})")

        # 简单的交易策略示例
        if random.random() < 0.1:  # 10% 概率发起交易
            await self.send_message(
                "market_maker",
                "TRADE_REQUEST",
                {
                    "symbol": symbol,
                    "quantity": random.randint(1, 10),
                    "price": price
                }
            )

    async def _handle_greeting(self, sender: str, payload: Dict[str, Any]):
        """处理问候消息"""
        message = payload.get("message", "")
        self.logger.info(f"Received greeting from {sender}: {message}")

        # 回复问候
        await self.send_message(
            sender,
            "GREETING_REPLY",
            {
                "message": f"Hello {sender}! I'm {self.agent_id}, nice to meet you!",
                "portfolio_value": self._calculate_portfolio_value()
            }
        )

    def _calculate_portfolio_value(self) -> float:
        """计算投资组合总价值（简化版）"""
        return self.portfolio["cash"] + sum(
            quantity * 100.0  # 假设每股100美元
            for quantity in self.portfolio["positions"].values()
        )

    async def handle_time_tick(self, payload: Dict[str, Any]):
        """处理时间同步事件"""
        await super().handle_time_tick(payload)

        # 在每个时间刻度执行一些逻辑
        if self.current_tick_id and self.current_tick_id % 10 == 0:
            portfolio_value = self._calculate_portfolio_value()
            self.logger.info(
                f"Portfolio update at tick {self.current_tick_id}: "
                f"Cash=${self.portfolio['cash']:.2f}, "
                f"Total Value=${portfolio_value:.2f}"
            )
