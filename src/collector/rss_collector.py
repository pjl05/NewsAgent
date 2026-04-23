from __future__ import annotations

import feedparser
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any

from .base import BaseCollector


class RSSCollector(BaseCollector):
    """RSS/Atom 订阅源采集器（免费，无 API Key）"""

    DEFAULT_FEEDS: List[str] = [
        "https://36kr.com/feed",
        "https://www.huxiu.com/rss/feed.xml",
        "https://sspai.com/feed",
        "https://www.zhihu.com/rss",
    ]

    def collect(self, sources: List[str] | None = None) -> List[Dict[str, Any]]:
        sources = sources or self.DEFAULT_FEEDS
        results: List[Dict[str, Any]] = []
        for source in sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries:
                    item = self._parse_entry(entry, feed.feed, source)
                    if item:
                        results.append(item)
            except Exception as e:
                print(f"[RSSCollector] Error parsing {source}: {e}")
                continue
        return results

    def _parse_entry(
        self, entry: feedparser.FeedParserEntry, feed: feedparser.Feed, source: str
    ) -> Dict[str, Any] | None:
        link = entry.get("link", "")
        if not link:
            return None

        content_id = f"rss_{hashlib.md5(link.encode()).hexdigest()[:12]}"
        published_at = self._parse_date(entry)
        summary = entry.get("summary", "") or entry.get("description", "")
        if len(summary) > 500:
            summary = summary[:500] + "..."

        return {
            "content_id": content_id,
            "title": entry.get("title", "Untitled"),
            "source": feed.get("title", source),
            "url": link,
            "published_at": published_at,
            "summary": self._clean_html(summary),
            "tags": self._extract_tags(entry),
        }

    def _parse_date(self, entry: feedparser.FeedParserEntry) -> datetime:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except Exception:
                pass
        return datetime.utcnow()

    def _clean_html(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_tags(self, entry: feedparser.FeedParserEntry) -> List[str]:
        tags: List[str] = []
        for tag in entry.get("tags", []):
            term = tag.get("term", "")
            if term:
                tags.append(term)
        return tags