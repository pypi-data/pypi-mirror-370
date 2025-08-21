"""
Celery application configuration.
"""

from celery import Celery

# Initialize Celery app
app = Celery("task_dispatcher")

# Load configuration
app.config_from_object("task_dispatcher.config.celeryconfig")

# Auto-discover tasks
app.autodiscover_tasks(["task_dispatcher.tasks"], force=True)
