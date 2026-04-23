from __future__ import annotations

from typing import List, Dict, Any

from src.worker.celery_app import celery_app
from src.collector.rss_collector import RSSCollector
from src.collector.platform_collector import PlatformCollector
from src.collector.search_collector import SearchCollector
from src.collector.dedup import deduplicate_content
from src.db.database import get_db
from src.models.content import Content


@celery_app.task
def collect_rss() -> Dict[str, int]:
    """定时采集 RSS 源"""
    collector = RSSCollector()
    items = collector.collect()
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}


@celery_app.task
def collect_platforms() -> Dict[str, int]:
    """定时采集微博/知乎热搜"""
    collector = PlatformCollector()
    items = collector.collect(["weibo", "zhihu"])
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}


@celery_app.task
def collect_search(queries: List[str]) -> Dict[str, int]:
    """手动触发搜索采集"""
    collector = SearchCollector()
    items = collector.collect(queries)
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}


def _save_contents(items: List[Dict[str, Any]]) -> None:
    """将内容写入 PostgreSQL（已存在则跳过）"""
    for item in items:
        db = next(get_db())
        try:
            existing = (
                db.query(Content)
                .filter_by(content_id=item["content_id"])
                .first()
            )
            if not existing:
                content = Content(**item)
                db.add(content)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()