import asyncio
import json
from collections.abc import Callable
from typing import Any

import aio_pika
import redis.asyncio as redis
import logging
from task_dispatcher.config import settings

from .sender import send_messages

logger = logging.getLogger(__name__)


class RedisAggregator:
    def __init__(self, redis_url, sources):
        self.redis_url = redis_url
        self.sources = set(sources)
        self.redis = None

    async def setup(self):
        if not self.redis:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def aggregate(self, source, task_id, body):
        await self.setup()
        key = f"agg:{task_id}"
        logger.info(f"Aggregating {source} for {task_id}")
        await self.redis.hset(key, source, json.dumps(body))
        await self.redis.expire(key, 86400)  # 1 day
        fields = await self.redis.hkeys(key)
        if set(fields) == self.sources:
            all_msgs = await self.redis.hgetall(key)
            await self.redis.delete(key)
            return [json.loads(all_msgs[src]) for src in self.sources]
        return None


class ConsumerManager:
    def __init__(
        self,
        main_func: Callable[[list[Any], aio_pika.IncomingMessage], Any | list[Any]],
        listen_queues: list[str],
        send_queues: list[str],
    ):
        self.main_func = main_func
        self.listen_queues = listen_queues
        self.send_queues = send_queues
        self.use_redis_agg = len(listen_queues) > 1
        self.aggregator = None
        if self.use_redis_agg:
            self.aggregator = RedisAggregator(
                redis_url=settings.rabbitmq.APP_MQ_AGGREGATOR_URL, sources=listen_queues
            )

    async def _wrapper(self):
        connection = await aio_pika.connect_robust(
            settings.rabbitmq.APP_MQ_CONNECTION_URL
        )
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        for idx, queue_name in enumerate(self.listen_queues):
            queue = await channel.declare_queue(queue_name, durable=True)

            async def handler(
                msg: aio_pika.IncomingMessage, qidx=idx, queue_name=queue_name
            ):
                try:
                    body = json.loads(msg.body.decode())
                except Exception as e:
                    logger.error(f"Failed to decode message from {queue_name}: {e}")
                    await msg.reject(requeue=False)
                    return

                task_id = body.get("task_id")
                if not task_id:
                    logger.warning(f"Missing task_id in message from {queue_name}")
                    await msg.reject(requeue=False)
                    return

                if self.use_redis_agg:
                    # 用Redis聚合
                    agg_result = await self.aggregator.aggregate(
                        queue_name, task_id, body
                    )
                    if agg_result is None:
                        return
                    messages = agg_result
                else:
                    # 单队列，直接处理
                    messages = [body]
                try:
                    result = await self.main_func(messages, msg)
                    if result is None:
                        # 消费者函数处理了消息确认，不需要自动确认
                        return
                    results = result if isinstance(result, list) else [result]

                    if len(results) != len(self.send_queues):
                        logger.warning(
                            f"Expected {len(self.send_queues)} outputs, got {len(results)}"
                        )
                        return

                    outbound = [
                        {"queue_name": self.send_queues[i], "message": results[i]}
                        for i in range(len(results))
                    ]
                    await send_messages(outbound, channel)
                    # 只有在成功发送到下游队列后才确认消息
                    await msg.ack()

                except Exception as e:
                    logger.exception(f"Exception in main: {e}")
                    await msg.reject(requeue=True)

            await queue.consume(handler)
            logger.info(f"Consuming from queue: {queue_name}")

        logger.info("All consumers started.")
        await asyncio.Future()

    def start(self):
        """启动消费者"""
        try:
            asyncio.run(self._wrapper())
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user.")

    def __call__(self, *args, **kwargs):
        """支持直接调用"""
        return self.main_func(*args, **kwargs)


def start_consumer(  # noqa: ANN201
    listen_queues: list[str],
    send_queues: list[str],
):
    def decorator(main: Callable[[list[Any]], Any | list[Any]]):
        return ConsumerManager(main, listen_queues, send_queues)

    return decorator
