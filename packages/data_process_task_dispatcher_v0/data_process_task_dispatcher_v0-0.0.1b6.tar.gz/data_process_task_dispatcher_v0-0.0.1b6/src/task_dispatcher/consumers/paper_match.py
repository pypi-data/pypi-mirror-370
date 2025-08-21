import logging
from typing import Any

import aio_pika
from task_dispatcher.tasks.tasks import process_paper_match
from task_dispatcher.mq.consumer import start_consumer
from task_dispatcher.celery_app import app # noqa: F401

logger = logging.getLogger(__name__)


@start_consumer(
    listen_queues=["queue.new_wos_paper_added_pipeline.crawl_paper.paper_match"],
    send_queues=[],
)
async def paper_match_consumer(
    messages: list[dict[str, Any]], message: aio_pika.IncomingMessage
) -> None:
    """
    轻量级消息转发器 - 只负责将消息转发给 Celery Worker
    优势：
    1. 可以随时重启部署，不影响正在执行的任务
    2. 消费者逻辑简单，出错概率低
    3. 任务执行与消费者解耦，可以独立扩缩容
    4. Worker 可以在不同机器上运行，实现真正的分布式
    """
    msg_data = messages[0]

    try:
        # 发送任务到 Celery Worker（独立进程/机器）
        task = process_paper_match.apply_async(args=[msg_data])
        logger.info(f"✅ Message forwarded to Celery worker: task_id={task.id}")
        # 立即确认消息 - 因为我们的职责只是转发
        await message.ack()
        logger.debug(f"✅ Message acknowledged: task_id={task.id}")
        return None

    except Exception as e:
        logger.error(f"❌ Failed to forward message to Celery: {e}")
        # 转发失败，拒绝消息并重新入队
        await message.reject(requeue=True)
        raise
