# Phase 6: 定时任务与可视化

**阶段：** Phase 6
**工期：** 2 周
**前置依赖：** Phase 2 + Phase 4 + Phase 5

---

## 6.1 阶段目标

完成定时任务调度和系统集成，包括：
1. APScheduler 定时任务配置
2. 每日批处理任务链
3. 系统集成测试
4. E2E 测试验证

**交付物：** 每周可视化报告，完整系统集成

---

## 6.2 定时任务架构

### 6.2.1 任务调度流程

```
22:00 ──→ daily_collection   (内容采集)
23:00 ──→ daily_embedding   (生成 Embedding)
01:00 ──→ daily_generation  (生成摘要/TTS)
07:30 ──→ daily_push         (推送日报)
周一 ──→ weekly_report       (推送周报)
```

### 6.2.2 核心任务设计

```python
# tasks.py
def daily_collection():
    from src.collector.rss_collector import RSSCollector
    from src.collector.search_collector import SearchCollector
    from src.db.database import get_db
    from src.models.content import Content
    collectors = [RSSCollector(), SearchCollector(), TianAPICollector()]
    all_content = []
    for collector in collectors:
        all_content.extend(collector.collect())
    with get_db() as db:
        for item in all_content:
            existing = db.query(Content).filter_by(content_id=item["content_id"]).first()
            if not existing:
                db.add(Content(**item))
        db.commit()
    return {"collected": len(all_content)}

def daily_embedding():
    from src.processor.embedder import ContentEmbedder
    from src.db.database import get_db
    from src.models.content import Content
    embedder = ContentEmbedder()
    with get_db() as db:
        contents = db.query(Content).filter(Content.embedding == None).all()
        for content in contents:
            content.embedding = embedder.embed(content.title + " " + (content.summary or ""))
        db.commit()
    return {"embedded": len(contents)}

def daily_push():
    from src.bot.pusher import ScheduledPusher
    from src.db.database import get_db
    from src.models.user import User
    pusher = ScheduledPusher()
    with get_db() as db:
        user_ids = [u.user_id for u in db.query(User).all()]
        pusher.push_daily(user_ids)
    return {"pushed": len(user_ids)}
```

### 6.2.3 Cron 配置

```python
# cron.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import daily_collection, daily_embedding, daily_push

def setup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_collection, CronTrigger(hour=22, minute=0), id="daily_collection")
    scheduler.add_job(daily_embedding, CronTrigger(hour=23, minute=0), id="daily_embedding")
    scheduler.add_job(daily_push, CronTrigger(hour=7, minute=30), id="daily_push")
    return scheduler
```

---

## 6.3 E2E 测试

```python
def test_full_content_flow():
    from src.collector.rss_collector import RSSCollector
    from src.processor.embedder import ContentEmbedder
    from src.recommender.engine import RecommendationEngine
    from src.recommender.collab import CollaborativeFilter

    collector = RSSCollector()
    items = collector.collect(["https://feeds.feedburner.com/36kr"])
    assert len(items) > 0

    embedder = ContentEmbedder()
    for item in items:
        item["embedding"] = embedder.embed(item["title"])

    collab = CollaborativeFilter()
    engine = RecommendationEngine(collab)
    ranked = engine.rank([0.1] * 128, items)
    assert ranked is not None
```

---

## 6.4 验收标准

| 检查项 | 标准 |
|--------|------|
| 定时任务 | 所有 cron 配置正确 |
| E2E 测试 | 完整流程测试通过 |
| 系统稳定 | 无致命错误或异常退出 |
