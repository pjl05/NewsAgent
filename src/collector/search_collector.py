from __future__ import annotations

import hashlib
from datetime import datetime
from typing import List, Dict, Any

import httpx
from bs4 import BeautifulSoup

from .base import BaseCollector
from src.config import get_settings

settings = get_settings()


class SearchCollector(BaseCollector):
    """搜索引擎采集器（Bing 免费 tier + DuckDuckGo 备选）"""

    async def collect(self, queries: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for query in queries:
            try:
                if settings.bing_api_key:
                    search_results = await self._search_bing(query)
                else:
                    search_results = await self._search_duckduckgo(query)
                results.extend(search_results)
            except Exception as e:
                print(
                    f"[SearchCollector] Bing failed for '{query}': {e}, "
                    "trying DuckDuckGo"
                )
                try:
                    search_results = await self._search_duckduckgo(query)
                    results.extend(search_results)
                except Exception as e2:
                    print(f"[SearchCollector] DuckDuckGo also failed: {e2}")
        return results

    async def _search_bing(self, query: str) -> List[Dict[str, Any]]:
        """Bing Search API（免费 tier，日限额）"""
        url = "https://api.bing.microsoft.com/v7.0/search"
        params = {"q": query, "count": 10, "mkt": "zh-CN"}
        headers = {"Ocp-Apim-Subscription-Key": settings.bing_api_key}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        results: List[Dict[str, Any]] = []
        for r in data.get("webPages", {}).get("value", []):
            link = r.get("url", "")
            results.append(
                {
                    "content_id": f"bing_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                    "title": r.get("name", ""),
                    "source": r.get("displayUrl", ""),
                    "url": link,
                    "published_at": datetime.now(),
                    "summary": r.get("snippet", "")[:500],
                    "tags": [query],
                }
            )
        return results

    async def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """DuckDuckGo HTML 抓取（无 API Key 要求）"""
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot)"}

        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: List[Dict[str, Any]] = []
        for r in soup.select(".result")[:10]:
            title_tag = r.select_one(".result__title a")
            snippet_tag = r.select_one(".result__snippet")
            if not title_tag:
                continue

            link = title_tag.get("href", "")
            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

            results.append(
                {
                    "content_id": f"ddg_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                    "title": title,
                    "source": "DuckDuckGo",
                    "url": link,
                    "published_at": datetime.now(),
                    "summary": snippet[:500],
                    "tags": [query],
                }
            )
        return results