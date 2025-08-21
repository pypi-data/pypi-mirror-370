import asyncio
from typing import Dict, Any
import random
import datetime
from agentlin.core.agent_message_queue import AgentMessage, AgentMessageQueue


class RandomMarket(AgentMessageQueue):
    """
    提供市场数据
    """

    def __init__(self, agent_id: str = "random_market", **kwargs):
        super().__init__(agent_id=agent_id, **kwargs)
        self.market_prices = {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
            "TSLA": 800.0,
            "MSFT": 300.0,
        }

    async def _handle_regular_message(self, msg: AgentMessage):
        """处理来自其他代理的消息"""
        sender = msg.sender
        message_type = msg.message_type
        payload = msg.payload or {}

        self.logger.info(f"Market maker received: {message_type} from {sender}")

        if message_type == "TRADE_REQUEST":
            await self._handle_trade_request(sender, payload)
        elif message_type == "GREETING":
            await self._handle_greeting(sender, payload)

    async def _handle_trade_request(self, sender: str, payload: Dict[str, Any]):
        """处理交易请求"""
        symbol = payload.get("symbol")
        quantity = payload.get("quantity", 0)
        requested_price = payload.get("price", 0.0)

        current_price = self.market_prices.get(symbol, 0.0)

        # 简单的价格匹配逻辑
        if abs(requested_price - current_price) / current_price < 0.05:  # 5% 价格容忍度
            await self.send_message(
                sender,
                "TRADE_CONFIRMATION",
                {
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "status": "FILLED",
                }
            )
            self.logger.info(f"Trade filled: {symbol} x {quantity} @ {current_price}")
        else:
            await self.send_message(
                sender,
                "TRADE_REJECTION",
                {
                    "symbol": symbol,
                    "quantity": quantity,
                    "requested_price": requested_price,
                    "current_price": current_price,
                    "reason": "Price out of range",
                }
            )

    async def _handle_greeting(self, sender: str, payload: Dict[str, Any]):
        """处理问候消息"""
        self.logger.info(f"Market maker greeting from {sender}")
        await self.send_message(
            sender,
            "GREETING_REPLY",
            {
                "message": f"Hello {sender}! I'm the market maker. Ready to trade!",
                "available_symbols": list(self.market_prices.keys())
            }
        )

    async def broadcast_market_data(self):
        """广播市场数据"""
        while not self._shutdown:
            for symbol in self.market_prices:
                # 模拟价格波动
                change = random.uniform(-0.02, 0.02)  # ±2% 变化
                self.market_prices[symbol] *= (1 + change)

                # 广播到所有交易者（这里简化为发送给特定代理）
                await self.publish_time(
                    "MARKET_DATA",
                    {
                        "symbol": symbol,
                        "price": self.market_prices[symbol],
                        "volume": random.randint(100, 1000),
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    },
                    "trader.market_data"
                )

            await asyncio.sleep(5)  # 每5秒更新一次
