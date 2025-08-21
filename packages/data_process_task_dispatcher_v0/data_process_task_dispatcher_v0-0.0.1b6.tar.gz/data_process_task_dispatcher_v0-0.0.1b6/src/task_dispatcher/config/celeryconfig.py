from kombu import Queue, Exchange
from task_dispatcher.config import settings

# Broker settings
broker_url = settings.celery.CELERY_BROKER_URL
result_backend = settings.celery.CELERY_RESULT_BACKEND
# result_backend = 'elasticsearch://elastic:6fYUYglM6Cj6rHgQkt6D@172.22.121.11:39200/celery_results'

# Task settings
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Shanghai"
enable_utc = True

# Queue settings
task_default_queue = "default"
task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
)

task_routes = {
    "tasks.process_paper_match": {"queue": "high_priority"},
}

# Task execution settings
task_track_started = True
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 100

# Logging
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"
