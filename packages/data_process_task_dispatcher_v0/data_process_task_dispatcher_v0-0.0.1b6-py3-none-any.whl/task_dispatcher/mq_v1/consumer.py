import asyncio
import json
from collections.abc import Callable
from typing import Any, Optional
from functools import wraps

import aio_pika
import redis.asyncio as redis
import logging

from .config import MQConfig, ConfigurationManager
from .sender import send_messages

logger = logging.getLogger(__name__)


class RedisAggregator:
    def __init__(self, redis_url: str, sources: list[str], consumer_name: str, message_ttl: int = 86400):
        self.redis_url = redis_url
        self.sources = set(sources)
        self.consumer_name = consumer_name
        self.redis = None
        self.message_ttl = message_ttl

    async def setup(self):
        if not self.redis:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def aggregate(self, source, task_id, body):
        await self.setup()
        key = f"agg:{self.consumer_name}:{task_id}"
        logger.info(f"Aggregating {source} for consumer {self.consumer_name}, task {task_id}")
        await self.redis.hset(key, source, json.dumps(body))
        await self.redis.expire(key, self.message_ttl)
        fields = await self.redis.hkeys(key)
        if set(fields) == self.sources:
            all_msgs = await self.redis.hgetall(key)
            await self.redis.delete(key)
            return [json.loads(all_msgs[src]) for src in self.sources]
        return None


class ConsumerManager:
    def __init__(
        self, 
        main_func: Callable[[list[Any]], Any | list[Any]], 
        listen_queues: list[str], 
        send_queues: list[str],
        config: Optional[MQConfig] = None,
        consumer_name: Optional[str] = None,
    ):
        self.main_func = main_func
        self.listen_queues = listen_queues
        self.send_queues = send_queues
        self._config = config
        self.use_redis_agg = len(listen_queues) > 1
        self.consumer_name = consumer_name or '-'.join(listen_queues)  # 如果没有提供consumer_name，使用队列名的组合
        self.aggregator = None

    @property
    def config(self) -> MQConfig:
        """延迟获取配置，直到真正需要时才获取"""
        if not hasattr(self, '_resolved_config'):
            self._resolved_config = self._config or ConfigurationManager.get_config()
            # 初始化聚合器
            if self.use_redis_agg:
                if not self._resolved_config.aggregator_url:
                    raise ValueError("Redis aggregator URL is required when using multiple listen queues")
                self.aggregator = RedisAggregator(
                    redis_url=self._resolved_config.aggregator_url, 
                    sources=self.listen_queues,
                    consumer_name=self.consumer_name,
                    message_ttl=self._resolved_config.message_ttl
                )
        return self._resolved_config

    async def _setup_dlx(self, channel: aio_pika.Channel, queue_name: str):
        """设置死信交换机和队列"""
        if not self.config.enable_dlx:
            return None, None

        dlx_name = f"{queue_name}.dlx"
        dlq_name = f"{queue_name}.dlq"
        
        # 声明死信交换机
        dlx = await channel.declare_exchange(
            dlx_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        logger.info(f"Declared dead letter exchange: {dlx_name}")
        
        # 声明死信队列
        dlq = await channel.declare_queue(
            dlq_name,
            durable=True,
            arguments={
                'x-message-ttl': self.config.message_ttl * 1000,  # 转换为毫秒
            }
        )
        logger.info(f"Declared dead letter queue: {dlq_name}")
        
        # 绑定死信队列到死信交换机
        await dlq.bind(dlx, routing_key=queue_name)
        logger.info(f"Bound {dlq_name} to {dlx_name} with routing key: {queue_name}")
        
        return dlx_name, dlq_name

    async def _wrapper(self):
        connection = await aio_pika.connect_robust(self.config.connection_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=self.config.prefetch_count)

        for idx, queue_name in enumerate(self.listen_queues):
            # 设置死信交换机
            dlx_name, dlq_name = await self._setup_dlx(channel, queue_name)
            
            # 声明队列，添加死信交换机配置
            queue_args = {}
            if self.config.enable_dlx:
                queue_args.update({
                    'x-dead-letter-exchange': dlx_name,
                    'x-dead-letter-routing-key': queue_name,
                })

            queue = await channel.declare_queue(
                queue_name, 
                durable=True,
                arguments=queue_args
            )

            async def handler(msg: aio_pika.IncomingMessage, qidx=idx, queue_name=queue_name):
                # 获取或初始化重试次数
                headers = msg.headers or {}
                retry_count = headers.get('x-retry-count', 0)
                
                try:
                    body = json.loads(msg.body.decode())
                except Exception as e:
                    logger.error(f"Failed to decode message from {queue_name}: {e}")
                    # 解码失败直接发送到死信队列
                    if self.config.enable_dlx:
                        logger.warning(f"Sending malformed message to DLQ {queue_name}.dlq (decode failed)")
                        await msg.reject(requeue=False)
                    else:
                        await msg.ack()
                    return

                try:
                    task_id = body.get("task_id")
                    if not task_id:
                        logger.warning(f"Missing task_id in message from {queue_name}")
                        # 缺少task_id直接发送到死信队列
                        if self.config.enable_dlx:
                            logger.warning(f"Sending message without task_id to DLQ {queue_name}.dlq")
                            await msg.reject(requeue=False)
                        else:
                            await msg.ack()
                        return

                    if self.use_redis_agg:
                        # 用Redis聚合
                        agg_result = await self.aggregator.aggregate(queue_name, task_id, body)
                        if agg_result is None:
                            await msg.ack()
                            return
                        messages = agg_result
                    else:
                        # 单队列，直接处理
                        messages = [body]

                    try:
                        result = await self.main_func(messages)
                        if result is None:
                            await msg.ack()
                            return

                        results = result if isinstance(result, list) else [result]

                        if len(results) != len(self.send_queues):
                            logger.warning(f"Expected {len(self.send_queues)} outputs, got {len(results)}")
                            await msg.ack()
                            return

                        outbound = [
                            {"queue_name": self.send_queues[i], "message": results[i]} for i in range(len(results))
                        ]
                        await send_messages(outbound, channel)
                        await msg.ack()

                    except asyncio.CancelledError:
                        logger.warning(f"Task {task_id} was cancelled")
                        await msg.nack(requeue=True)
                        return
                    except Exception as e:
                        logger.exception(f"Exception in main: {e}")
                        
                        # 检查重试次数
                        if retry_count >= self.config.max_retries:
                            logger.error(
                                f"Message {task_id} exceeded max retries ({self.config.max_retries}), "
                                f"sending to DLQ {queue_name}.dlq. Last error: {str(e)}"
                            )
                            if self.config.enable_dlx:
                                await msg.reject(requeue=False)
                            else:
                                await msg.ack()
                            return
                        
                        # 增加重试次数
                        retry_count += 1
                        headers['x-retry-count'] = retry_count
                        logger.warning(f"Retrying message {task_id} (attempt {retry_count}/{self.config.max_retries})")
                        
                        # 创建新消息用于重试
                        retry_message = aio_pika.Message(
                            body=msg.body,
                            headers=headers,
                            delivery_mode=msg.delivery_mode,
                            expiration=self.config.retry_delay  # 设置消息延迟
                        )
                        
                        # 重新发送到原队列
                        await channel.default_exchange.publish(
                            retry_message,
                            routing_key=queue_name
                        )
                        await msg.ack()  # 确认原消息
                        return

                except Exception as e:
                    logger.exception("Critical error in message handler")
                    # 确保消息在发生关键错误时也能被确认
                    await msg.ack()

            await queue.consume(handler)
            logger.info(f"Consuming from queue: {queue_name}")
            if self.config.enable_dlx:
                logger.info(f"Dead letter queue configured: {dlq_name}")

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
    config: Optional[MQConfig] = None,
    consumer_name: Optional[str] = None,
):
    """
    装饰器函数，用于创建和启动消息消费者

    Args:
        listen_queues: 要监听的队列列表
        send_queues: 要发送消息的队列列表
        config: 可选的MQ配置，如果不提供则使用全局配置
        consumer_name: 可选的消费者名称，用于Redis聚合时区分不同的消费者组合

    Example:
        @start_consumer(
            listen_queues=["input_queue"],
            send_queues=["output_queue"],
            config=MQConfig(
                connection_url="amqp://guest:guest@localhost/",
                prefetch_count=10
            )
        )
        async def process_message(messages: list[dict]) -> Any:
            # 处理消息
            return result
    """
    def decorator(main: Callable[[list[Any]], Any | list[Any]]):
        # 创建一个包装函数，延迟 ConsumerManager 的初始化
        @wraps(main)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, '_consumer'):
                wrapper._consumer = ConsumerManager(main, listen_queues, send_queues, config, consumer_name)
            return wrapper._consumer(*args, **kwargs)
        
        # 添加 start 方法
        wrapper.start = lambda: wrapper._consumer.start() if hasattr(wrapper, '_consumer') else ConsumerManager(main, listen_queues, send_queues, config, consumer_name).start()
        
        return wrapper

    return decorator
