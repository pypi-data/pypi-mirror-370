"""
Base task class for all Celery tasks.
"""

import time
from datetime import datetime
from celery import Task


class BaseTask(Task):
    """Base task class that provides common functionality for all tasks."""
    
    abstract = True  # This class is abstract and won't be registered as a task

    def __call__(self, *args, **kwargs):
        """Override to add timing and metadata to the task execution"""
        # 记录开始时间
        self._task_start_time = time.time()
        self._task_start_datetime = datetime.now().isoformat()
        
        try:
            # Execute the task
            result = super().__call__(*args, **kwargs)
            end_time = time.time()
            
            # Wrap the result with metadata
            return {
                "result": result,
                "task_metadata": {
                    "task_id": self.request.id,
                    "task_name": self.name,
                    "queue": self.request.delivery_info.get('routing_key', 'unknown'),
                    "retries": self.request.retries,
                    "max_retries": self.max_retries,
                    "args": args,
                    "kwargs": kwargs
                },
                "execution_info": {
                    "start_time": self._task_start_datetime,
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": round(end_time - self._task_start_time, 3),
                    "worker_pid": self.request.hostname,
                }
            }
            
        except Exception as exc:
            # 让异常继续传播，在 on_failure 中处理
            raise

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure by customizing error response"""
        # 计算执行时间
        execution_time = round(time.time() - getattr(self, '_task_start_time', time.time()), 3)
        
        # 构建自定义错误信息
        error_info = {
            "exc_type": type(exc).__name__,
            "exc_message": [str(exc)],  # 保持与原始格式一致
            "exc_module": type(exc).__module__,
            "error_metadata": {
                "task_id": task_id,
                "task_name": self.name,
                "queue": self.request.delivery_info.get('routing_key', 'unknown'),
                "retries": self.request.retries,
                "max_retries": self.max_retries,
                "execution_time": execution_time,
                "worker_pid": self.request.hostname,
                "args": args,
                "kwargs": kwargs
            }
        }
        
        # 更新任务结果
        self.update_state(
            state="FAILURE",
            meta=error_info
        )
        
        super().on_failure(exc, task_id, args, kwargs, einfo) 