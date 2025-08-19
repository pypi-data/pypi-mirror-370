"""Queue extension module.

Sets up Celery for asynchronous task processing with Flask integration
and comprehensive task monitoring capabilities.
"""

from typing import TYPE_CHECKING

from celery import Celery, Task
from flask import Flask

if TYPE_CHECKING:
    from flask_restx import Api

celery = Celery()


def get_task_monitoring_namespace() -> tuple:
    """Get the task monitoring namespace for API registration.

    Returns:
        A tuple of (namespace, path) for registering with Flask-RESTX API.

    """
    from zecmf.api.task_monitoring import task_monitoring_namespace  # noqa: PLC0415

    return (task_monitoring_namespace, "/task-monitoring")


def register_monitoring_api(api: "Api") -> None:
    """Register the task monitoring API namespace with an existing API instance.

    Args:
        api: The Flask-RESTX API instance to register the namespace with.

    """
    namespace, path = get_task_monitoring_namespace()
    api.add_namespace(namespace, path=path)


def init_app(app: Flask) -> None:
    """Initialize Celery with the Flask app and task monitoring."""
    # Get configuration from app config with defaults
    broker_url = app.config.get("CELERY_BROKER_URL", "memory://")
    result_backend = app.config.get("CELERY_RESULT_BACKEND", "cache")

    # Task monitoring configuration
    enable_monitoring = app.config.get("CELERY_TASK_MONITORING", True)

    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_track_started=True,
        task_time_limit=app.config.get("CELERY_TASK_TIME_LIMIT", 1800),  # 30 minutes
        worker_max_tasks_per_child=app.config.get("CELERY_WORKER_MAX_TASKS", 100),
        broker_connection_retry_on_startup=True,
        # Enhanced monitoring settings
        task_send_sent_event=enable_monitoring,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    class ContextTask(Task):
        """Base task class that ensures tasks run within a Flask app context."""

        def __call__(self, *args: object, **kwargs: object) -> object:
            """Execute task within the Flask application context.

            Wrapping ``super().__call__`` instead of calling ``self.run``
            directly preserves Celery's built-in request handling, retries and
            signal dispatching while still ensuring that a Flask application
            context is active during task execution.
            """
            with app.app_context():
                return super().__call__(*args, **kwargs)

    # Assign ContextTask directly to the Celery application
    celery.Task = ContextTask

    # Set ContextTask as the default task base class
    celery.conf.update(task_default_queue="default")

    # Set up task monitoring if enabled
    if enable_monitoring:
        # Make Flask app available to task monitor
        from zecmf.extensions import task_monitor  # noqa: PLC0415

        task_monitor.flask_app = app
