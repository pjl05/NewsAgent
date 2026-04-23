from __future__ import annotations

import hashlib
from datetime import datetime
from typing import List, Dict, Any

import httpx

from .base import BaseCollector


class PlatformCollector(BaseCollector):
    """垂直平台热搜采集器（免费 API，无需认证）"""

    async def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for source in sources:
            try:
                if source == "weibo":
                    results.extend(await self._fetch_weibo())
                elif source == "zhihu":
                    results.extend(await self._fetch_zhihu())
            except Exception as e:
                print(f"[PlatformCollector] Error fetching {source}: {e}")
                continue
        return results

    async def _fetch_weibo(self) -> List[Dict[str, Any]]:
        """微博热搜（无需认证）"""
        url = "https://weibo.com/ajax/side/hotSearch"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        results: List[Dict[str, Any]] = []
        for item in data.get("data", {}).get("realtime", [])[:20]:
            title = item.get("word", "")
            if not title:
                continue
            results.append(
                {
                    "content_id": f"weibo_{hashlib.md5(title.encode()).hexdigest()[:12]}",
                    "title": title,
                    "source": "微博热搜",
                    "url": f"https://s.weibo.com/weibo?q={title}",
                    "published_at": datetime.now(),
                    "summary": item.get("raw_hot", ""),
                    "tags": ["微博热搜"],
                }
            )
        return results

    async def _fetch_zhihu(self) -> List[Dict[str, Any]]:
        """知乎热榜（无需认证）"""
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        results: List[Dict[str, Any]] = []
        for item in data.get("data", [])[:20]:
            target = item.get("target", {})
            title = target.get("title", "")
            if not title:
                continue
            results.append(
                {
                    "content_id": f"zhihu_{hashlib.md5(title.encode()).hexdigest()[:12]}",
                    "title": title,
                    "source": "知乎热榜",
                    "url": target.get("url", ""),
                    "published_at": datetime.now(),
                    "summary": target.get("excerpt", ""),
                    "tags": ["知乎热榜"],
                }
            )
        return results