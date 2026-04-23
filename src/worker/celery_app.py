from celery import Celery
from celery.schedules import crontab

from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "newsagent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.worker.tasks"],
)

celery_app.conf.update(
    timezone="Asia/Shanghai",
    beat_schedule={
        "collect-rss-daily": {
            "task": "src.worker.tasks.collect_rss",
            "schedule": crontab(hour=22, minute=0),
        },
        "collect-platforms-daily": {
            "task": "src.worker.tasks.collect_platforms",
            "schedule": crontab(hour=22, minute=30),
        },
    },
)