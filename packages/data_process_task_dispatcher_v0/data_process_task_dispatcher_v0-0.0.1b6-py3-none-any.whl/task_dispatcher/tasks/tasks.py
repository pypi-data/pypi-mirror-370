"""
Celery tasks definitions.
"""

import asyncio
import logging
from celery import shared_task
from task_dispatcher.services.a import execute
from task_dispatcher.tasks.base import BaseTask

logger = logging.getLogger(__name__)


@shared_task(
    name="tasks.process_paper_match",
    queue="high_priority",
    bind=True,
    max_retries=3,
    acks_late=True,
    base=BaseTask,
)
def process_paper_match(self, args: dict) -> dict:
    task_id = self.request.id
    logger.info(f"[{self.request.id}] 当前是第 {self.request.retries} 次重试")
    logger.info(f"🚀 Starting task {task_id}")

    try:
        # 执行核心业务逻辑
        result = asyncio.run(execute(args))
        logger.info(f"Task {task_id} completed successfully")
        return result
    except Exception as exc:
        logger.error(f"Task {task_id} failed: {exc}")
        # 不需要传递额外的kwargs，BaseTask会自动处理
        raise self.retry(exc=exc, countdown=5)
