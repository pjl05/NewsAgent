from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)

TIANAPI_BASE = "https://apis.tianapi.com"


class TianAPICollector:
    """天行数据(TianAPI)热搜采集器
    覆盖微博热搜、抖音热搜、全网热搜（百度为主）
    API免费额度：100次/天，数据实时更新
    """

    # 抖音标签映射
    LABEL_MAP = {
        0: "普通",
        1: "新",
        3: "热",
        8: "推荐",
        16: "视频",
    }

    def __init__(self) -> None:
        settings = get_settings()
        self.key = settings.tianapi_key
        self._http_timeout = 15.0

    async def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        """采集指定平台的热搜数据"""
        results: List[Dict[str, Any]] = []
        for source in sources:
            try:
                if source == "weibo":
                    results.extend(await self._fetch_weibo())
                elif source == "douyin":
                    results.extend(await self._fetch_douyin())
                elif source == "baidu":
                    results.extend(await self._fetch_baidu())
                elif source == "zhihu":
                    results.extend(await self._fetch_zhihu_from_network())
            except Exception as e:
                logger.warning("[TianAPICollector] Error fetching %s: %s", source, e)
                continue
        return results

    def _make_content_id(self, prefix: str, title: str) -> str:
        return f"{prefix}_{hashlib.md5(title.encode()).hexdigest()[:12]}"

    def _build_item(
        self,
        content_id: str,
        title: str,
        source: str,
        url: str,
        summary: str,
        hot_value: str,
        tag: str,
    ) -> Dict[str, Any]:
        return {
            "content_id": content_id,
            "title": title,
            "source": source,
            "url": url or "",
            "published_at": datetime.now(),
            "summary": summary or hot_value or "",
            "tags": [tag] if tag else [source],
        }

    async def _fetch_weibo(self) -> List[Dict[str, Any]]:
        """微博热搜"""
        url = f"{TIANAPI_BASE}/weibohot/index"
        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()

        if data.get("code") != 200:
            logger.warning("[TianAPICollector] weibo API error: %s", data.get("msg"))
            return []

        items = data.get("result", {}).get("list", [])
        results: List[Dict[str, Any]] = []
        for item in items:
            title = item.get("hotword", "").strip()
            if not title:
                continue
            hot_value = item.get("hotwordnum", "").strip()
            hottag = item.get("hottag", "").strip()
            results.append(
                self._build_item(
                    content_id=self._make_content_id("weibo", title),
                    title=title,
                    source="微博热搜",
                    url=f"https://s.weibo.com/weibo?q={title}",
                    summary=hottag,
                    hot_value=hot_value,
                    tag=hottag or "微博热搜",
                )
            )
        logger.info("[TianAPICollector] weibo: got %d items", len(results))
        return results

    async def _fetch_douyin(self) -> List[Dict[str, Any]]:
        """抖音热搜"""
        url = f"{TIANAPI_BASE}/douyinhot/index"
        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()

        if data.get("code") != 200:
            logger.warning("[TianAPICollector] douyin API error: %s", data.get("msg"))
            return []

        items = data.get("result", {}).get("list", [])
        results: List[Dict[str, Any]] = []
        for item in items:
            title = item.get("word", "").strip()
            if not title:
                continue
            hot_index = item.get("hotindex", 0)
            label = item.get("label", 0)
            tag = self.LABEL_MAP.get(label, str(label))
            results.append(
                self._build_item(
                    content_id=self._make_content_id("douyin", title),
                    title=title,
                    source="抖音热搜",
                    url=f"https://www.douyin.com/search/{title}",
                    summary=f"热度指数: {hot_index}",
                    hot_value=str(hot_index),
                    tag=f"抖音{tag}",
                )
            )
        logger.info("[TianAPICollector] douyin: got %d items", len(results))
        return results

    async def _fetch_baidu(self) -> List[Dict[str, Any]]:
        """百度热搜（通过全网热搜接口）"""
        url = f"{TIANAPI_BASE}/networkhot/index"
        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()

        if data.get("code") != 200:
            logger.warning("[TianAPICollector] baidu API error: %s", data.get("msg"))
            return []

        items = data.get("result", {}).get("list", [])
        results: List[Dict[str, Any]] = []
        for item in items:
            title = item.get("title", "").strip()
            if not title:
                continue
            hot_num = item.get("hotnum", 0)
            digest = item.get("digest", "").strip()
            results.append(
                self._build_item(
                    content_id=self._make_content_id("baidu", title),
                    title=title,
                    source="百度热搜",
                    url=f"https://www.baidu.com/s?wd={title}",
                    summary=digest,
                    hot_value=str(hot_num),
                    tag="百度热搜",
                )
            )
        logger.info("[TianAPICollector] baidu: got %d items", len(results))
        return results

    async def _fetch_zhihu_from_network(self) -> List[Dict[str, Any]]:
        """知乎热榜（通过全网热搜接口，数据源主要为百度）"""
        # TianAPI 的全网热搜以百度为主，知乎数据通过聚合方式获取
        # 如需更精确的知乎数据，可申请单独知乎接口
        return await self._fetch_baidu()
