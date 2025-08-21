import json
import logging
from typing import Any, Optional

import aio_pika

from .config import MQConfig, ConfigurationManager

logger = logging.getLogger(__name__)


class MessageSender:
    def __init__(self, config: Optional[MQConfig] = None):
        self.config = config or ConfigurationManager.get_config()
        self.connection = None
        self.channel = None

    async def setup(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.config.connection_url)
            self.channel = await self.connection.channel()

    async def send_message(self, data: dict[str, str], queue: str) -> bool:
        """
        发送单条消息到指定队列

        Args:
            data: 要发送的消息数据
            queue: 目标队列名称

        Returns:
            bool: 发送是否成功
        """
        try:
            # 确保连接已建立
            await self.setup()
            
            # 序列化消息
            payload = json.dumps(data).encode()
            
            # 发送消息
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=payload,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=queue,
            )
            
            logger.info(f"Successfully sent message to queue: {queue}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to serialize message data: {str(e)}")
            return False
        except aio_pika.exceptions.AMQPError as e:
            logger.error(f"Failed to send message to queue {queue}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message to {queue}: {str(e)}")
            return False

    async def send_messages(self, messages: list[dict[str, Any]]):
        """
        发送消息到指定队列

        Args:
            messages: 消息列表，每个消息是一个字典，包含 queue_name 和 message 字段
        """
        if not messages:
            return

        await self.setup()
        
        for msg in messages:
            try:
                queue_name = msg["queue_name"]
                payload = json.dumps(msg["message"]).encode()

                await self.channel.default_exchange.publish(
                    aio_pika.Message(body=payload, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key=queue_name,
                )
                logger.info(f"Sent message to queue: {queue_name}")

            except Exception as e:
                logger.exception(f"Failed to send message to {msg.get('queue_name')}: {e}")

    async def close(self):
        """关闭连接"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None


# 为了保持向后兼容性，保留原有的函数
async def send_messages(messages: list[dict[str, Any]], channel: aio_pika.Channel):
    """
    发送消息到指定队列（旧版本兼容函数）

    Args:
        messages: 消息列表，每个消息是一个字典，包含 queue_name 和 message 字段
        channel: RabbitMQ channel 对象
    """
    if not messages:
        return

    for msg in messages:
        try:
            queue_name = msg["queue_name"]
            payload = json.dumps(msg["message"]).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(body=payload, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
            logger.info(f"Sent message to queue: {queue_name}")

        except Exception as e:
            logger.exception(f"Failed to send message to {msg.get('queue_name')}: {e}")
