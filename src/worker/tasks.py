from __future__ import annotations

import asyncio
import logging
from typing import List, Dict, Any

from src.worker.celery_app import celery_app
from src.collector.rss_collector import RSSCollector
from src.collector.tianapi_collector import TianAPICollector
from src.collector.search_collector import SearchCollector
from src.collector.dedup import deduplicate_content
from src.db.database import get_db
from src.models.content import Content

logger = logging.getLogger(__name__)


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
    """定时采集微博/抖音/百度热搜（通过 TianAPI）"""
    collector = TianAPICollector()
    items = asyncio.run(collector.collect(["weibo", "douyin", "baidu"]))
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}


@celery_app.task
def collect_search(queries: List[str]) -> Dict[str, int]:
    """手动触发搜索采集"""
    collector = SearchCollector()
    items = asyncio.run(collector.collect(queries))
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}


def _save_contents(items: List[Dict[str, Any]]) -> None:
    """将内容写入 PostgreSQL（已存在则跳过）"""
    if not items:
        return

    for item in items:
        try:
            with get_db() as db:
                existing = (
                    db.query(Content)
                    .filter_by(content_id=item["content_id"])
                    .first()
                )
                if not existing:
                    content = Content(**item)
                    db.add(content)
                    db.commit()
        except Exception as e:
            logger.error(
                "[_save_contents] Failed to save content %s: %s",
                item.get("content_id"),
                e,
            )