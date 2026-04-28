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
from src.recommender.embedder import ContentEmbedder
from src.generator.summarizer import Summarizer
from src.generator.tts_generator import TTSGenerator

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


@celery_app.task
def daily_embedding_task() -> Dict[str, int]:
    """每天 23:00 — 为没有 embedding 的内容生成向量"""
    embedder = ContentEmbedder()
    embedded_count = 0

    with get_db() as db:
        contents = db.query(Content).filter(Content.embedding.is_(None)).all()

    for content in contents:
        try:
            content_dict = {
                "content_id": content.content_id,
                "title": content.title,
                "summary": content.summary,
            }
            # ContentEmbedder.embed_content is async, wrap with asyncio.run()
            result = asyncio.run(embedder.embed_content(content_dict))
            embedding = result.get("embedding")

            if embedding:
                with get_db() as db:
                    db_content = db.query(Content).filter_by(content_id=content.content_id).first()
                    if db_content:
                        db_content.embedding = embedding
                        db.commit()
                embedded_count += 1
                logger.info("Embedded content %s", content.content_id)
        except Exception as e:
            logger.error("Failed to embed content %s: %s", content.content_id, e)

    return {"embedded": embedded_count}


@celery_app.task
def daily_generation_task() -> Dict[str, int]:
    """每天 01:00 — 为没有 summary 的内容生成摘要，并生成 TTS"""
    summarizer = Summarizer()
    tts_generator = TTSGenerator()
    summarized_count = 0
    tts_generated_count = 0

    with get_db() as db:
        # 内容 without summary
        contents_needing_summary = (
            db.query(Content).filter(Content.summary.is_(None)).all()
        )

    # Step 1: generate summaries
    for content in contents_needing_summary:
        try:
            text_to_summarize = content.title or ""
            summary_text = asyncio.run(summarizer.summarize(text_to_summarize))

            if summary_text:
                with get_db() as db:
                    db_content = (
                        db.query(Content).filter_by(content_id=content.content_id).first()
                    )
                    if db_content:
                        db_content.summary = summary_text
                        db.commit()
                summarized_count += 1
                logger.info("Summarized content %s", content.content_id)
        except Exception as e:
            logger.error("Failed to summarize content %s: %s", content.content_id, e)

    # Step 2: generate TTS for contents without audio_url
    with get_db() as db:
        contents_needing_tts = (
            db.query(Content)
            .filter(Content.summary.isnot(None), Content.audio_url.is_(None))
            .all()
        )

    for content in contents_needing_tts:
        try:
            audio_path = tts_generator.generate(content.summary)

            if audio_path:
                with get_db() as db:
                    db_content = (
                        db.query(Content).filter_by(content_id=content.content_id).first()
                    )
                    if db_content:
                        db_content.audio_url = audio_path
                        db.commit()
                tts_generated_count += 1
                logger.info("TTS generated for content %s", content.content_id)
        except Exception as e:
            logger.error("Failed to generate TTS for content %s: %s", content.content_id, e)

    return {"summarized": summarized_count, "tts_generated": tts_generated_count}


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


