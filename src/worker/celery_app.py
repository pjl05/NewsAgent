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
        # Phase 5: WeChat 定时推送
        "push-daily-summary": {
            "task": "src.worker.tasks.push_daily_summary_task",
            "schedule": crontab(hour=8, minute=0),
        },
        "push-weekly-report": {
            "task": "src.worker.tasks.push_weekly_report_task",
            "schedule": crontab(hour=9, minute=0, day_of_week=1),
        },
        # Phase 6: 每日 embedding 生成
        "daily-embedding": {
            "task": "src.worker.tasks.daily_embedding_task",
            "schedule": crontab(hour=23, minute=0),
        },
        # Phase 6: 每日摘要/TTS 生成
        "daily-generation": {
            "task": "src.worker.tasks.daily_generation_task",
            "schedule": crontab(hour=1, minute=0),
        },
    },
)