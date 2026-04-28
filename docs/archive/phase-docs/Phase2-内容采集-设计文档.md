# Phase 2: 内容采集

**阶段：** Phase 2
**工期：** 2 周
**前置依赖：** Phase 1

---

## 2.1 阶段目标

实现全网内容自动采集系统，**全部采用免费方案，无强制付费 API**。

| 来源 | 方式 | 优先级 | 备注 |
|------|------|--------|------|
| 中文 RSS 源 | feedparser | P0（主力） | 无需 API Key |
| 微博热搜 | TianAPI weibohot | P0 | 100次/天，实时 |
| 抖音热搜 | TianAPI douyinhot | P0 | 100次/天，每3分钟更新 |
| 百度热搜 | TianAPI networkhot | P0 | 100次/天，实时 |
| Bing Search | httpx | P1（搜索采集用） | 免费 tier，备用 |
| DuckDuckGo | httpx + BeautifulSoup | P1 | 无限额备选 |

**交付物：** 自动化内容采集管道，每日可采集数百条内容

> **2026-04-23 更新**：原 PlatformCollector（直接调用微博/知乎 API）因平台加认证已失效，改为 TianAPI 聚合方案，额外新增抖音热搜采集。

---

## 2.2 技术架构

### 2.2.1 采集器架构

```
┌─────────────────────────────────────────────────────────────┐
│                    采集层 (Collector)                       │
├───────────────┬──────────────────┬──────────────────────────┤
│  RSSCollector │ SearchCollector  │ TianAPICollector        │
│  (feedparser) │ (Bing/DuckDuckGo)│ (微博/抖音/百度热搜)    │
├───────────────┴──────────────────┴──────────────────────────┤
│                      内容标准化                              │
│         title / source / url / published_at / summary       │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌─────────────────┐
                    │  内容去重        │
                    │  (content_id)   │
                    └─────────────────┘
                            ↓
                    ┌─────────────────┐
                    │  数据库存储     │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

### 2.2.2 采集数据流程

```
定时任务 (Celery Beat)
     │
     ├─→ 1. RSS 采集
     │      ├─ 36kr RSS: https://36kr.com/feed
     │      ├─ 虎嗅 RSS: https://www.huxiu.com/rss/feed.xml
     │      ├─ 少数派 RSS: https://sspai.com/feed
     │      └─ 更多 RSS 源...
     │
     ├─→ 2. 热搜榜 API 采集 (TianAPI)
     │      ├─ 微博热搜: apis.tianapi.com/weibohot/index
     │      ├─ 抖音热搜: apis.tianapi.com/douyinhot/index
     │      └─ 百度热搜: apis.tianapi.com/networkhot/index
     │
     └─→ 3. 搜索补充采集
            ├─ Bing Search (免费 tier，每日有限额)
            └─ DuckDuckGo (备选，无限额)
```

> **热搜 API 免费额度：100 次/天**，每天采集 3 次（RSS + 热搜 + 搜索）完全够用。

---

## 2.3 目录结构

```
src/collector/
├── __init__.py
├── base.py                  # 抽象基类
├── rss_collector.py         # RSS 采集（P0）
├── search_collector.py      # 搜索引擎采集（Bing/DuckDuckGo）
├── tianapi_collector.py     # TianAPI 热搜采集（微博/抖音/百度）
└── dedup.py                 # 内容去重

src/worker/
├── __init__.py
├── celery_app.py           # Celery 应用配置
└── tasks.py                # 采集任务定义
```

---

## 2.4 核心模块设计

### 2.4.1 BaseCollector

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """采集器抽象基类"""

    @abstractmethod
    def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        从给定来源采集内容

        Returns:
            内容列表，每项包含:
            - content_id: 唯一标识
            - title: 标题
            - source: 来源平台
            - url: 原文链接
            - published_at: 发布时间
            - summary: 摘要
            - tags: 标签
        """
        pass
```

### 2.4.2 RSSCollector

使用 `feedparser` 解析 RSS/Atom 订阅源，标准库依赖无需额外 API Key。

```python
import feedparser
from datetime import datetime
import hashlib
from .base import BaseCollector

class RSSCollector(BaseCollector):
    """RSS/Atom 订阅源采集器（免费，无 API Key）"""

    DEFAULT_FEEDS = [
        "https://36kr.com/feed",
        "https://www.huxiu.com/rss/feed.xml",
        "https://sspai.com/feed",
    ]

    def collect(self, sources: List[str] | None = None) -> List[Dict[str, Any]]:
        sources = sources or self.DEFAULT_FEEDS
        results = []
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

    def _parse_entry(self, entry, feed, source) -> Dict[str, Any] | None:
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

    def _parse_date(self, entry) -> datetime:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except Exception:
                pass
        return datetime.utcnow()

    def _clean_html(self, text: str) -> str:
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_tags(self, entry) -> List[str]:
        tags = []
        for tag in entry.get("tags", []):
            term = tag.get("term", "")
            if term:
                tags.append(term)
        return tags
```

### 2.4.3 TianAPICollector

通过天行数据（TianAPI）聚合接口获取微博/抖音/百度热搜，完全免费且稳定。

```python
import httpx
from datetime import datetime
import hashlib
from .base import BaseCollector

TIANAPI_BASE = "https://apis.tianapi.com"

class TianAPICollector(BaseCollector):
    """天行数据热搜采集器（微博/抖音/百度，100次/天免费）"""

    LABEL_MAP = {0: "普通", 1: "新", 3: "热", 8: "推荐", 16: "视频"}

    def __init__(self):
        settings = get_settings()
        self.key = settings.tianapi_key  # 配置 TIANAPI_KEY

    async def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        results = []
        for source in sources:
            try:
                if source == "weibo":
                    results.extend(await self._fetch_weibo())
                elif source == "douyin":
                    results.extend(await self._fetch_douyin())
                elif source == "baidu":
                    results.extend(await self._fetch_baidu())
            except Exception as e:
                print(f"[TianAPICollector] Error fetching {source}: {e}")
                continue
        return results

    async def _fetch_weibo(self) -> List[Dict[str, Any]]:
        """微博热搜"""
        url = f"{TIANAPI_BASE}/weibohot/index"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()
        # 返回 50 条，字段: hotword, hotwordnum, hottag
        ...

    async def _fetch_douyin(self) -> List[Dict[str, Any]]:
        """抖音热搜（每3分钟更新）"""
        url = f"{TIANAPI_BASE}/douyinhot/index"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()
        # 返回 50 条，字段: word, hotindex, label (标签:新/热/荐/视频)
        ...

    async def _fetch_baidu(self) -> List[Dict[str, Any]]:
        """百度热搜（全网热搜聚合）"""
        url = f"{TIANAPI_BASE}/networkhot/index"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params={"key": self.key, "num": 50})
            response.raise_for_status()
            data = response.json()
        # 返回 50 条，字段: title, hotnum, digest
        ...
```

### 2.4.4 SearchCollector

先用 Bing Search 免费 tier，不够用再走 DuckDuckGo 备选。

```python
import httpx
from datetime import datetime
import hashlib
from .base import BaseCollector
from src.config import get_settings

settings = get_settings()

class SearchCollector(BaseCollector):
    """搜索引擎采集器（Bing 免费 + DuckDuckGo 备选）"""

    async def collect(self, queries: List[str]) -> List[Dict[str, Any]]:
        results = []
        for query in queries:
            try:
                search_results = await self._search_bing(query)
                results.extend(search_results)
            except Exception as e:
                print(f"[SearchCollector] Bing failed for '{query}': {e}, trying DuckDuckGo")
                try:
                    search_results = await self._search_duckduckgo(query)
                    results.extend(search_results)
                except Exception as e2:
                    print(f"[SearchCollector] DuckDuckGo also failed: {e2}")
        return results

    async def _search_bing(self, query: str) -> List[Dict[str, Any]]:
        """Bing Search API（免费 tier）"""
        if not settings.bing_api_key:
            raise ValueError("BING_API_KEY not configured")

        url = "https://api.bing.microsoft.com/v7.0/search"
        params = {"q": query, "count": 10, "mkt": "zh-CN"}
        headers = {"Ocp-Apim-Subscription-Key": settings.bing_api_key}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        for r in data.get("webPages", {}).get("value", []):
            link = r.get("url", "")
            results.append({
                "content_id": f"bing_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                "title": r.get("name", ""),
                "source": r.get("displayUrl", ""),
                "url": link,
                "published_at": datetime.utcnow(),
                "summary": r.get("snippet", "")[:500],
                "tags": [query],
            })
        return results

    async def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """DuckDuckGo HTML 抓取（无 API Key 要求）"""
        from bs4 import BeautifulSoup

        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot)"}

        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for r in soup.select(".result")[:10]:
            title_tag = r.select_one(".result__title a")
            snippet_tag = r.select_one(".result__snippet")
            if not title_tag:
                continue

            link = title_tag.get("href", "")
            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

            results.append({
                "content_id": f"ddg_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                "title": title,
                "source": "DuckDuckGo",
                "url": link,
                "published_at": datetime.utcnow(),
                "summary": snippet[:500],
                "tags": [query],
            })
        return results
```

---

## 2.5 内容去重策略

```python
def deduplicate_content(all_content: List[Dict]) -> List[Dict]:
    """基于 content_id 去重"""
    seen_ids = set()
    unique_content = []

    for item in all_content:
        content_id = item.get("content_id")
        if content_id and content_id not in seen_ids:
            seen_ids.add(content_id)
            unique_content.append(item)

    return unique_content
```

---

## 2.6 Celery 定时任务

### 2.6.1 Celery 配置

```python
# src/worker/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "newsagent",
    broker=settings.celery_broker_url,  # Redis
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    timezone="Asia/Shanghai",
    beat_schedule={
        "collect-rss-daily": {
            "task": "src.worker.tasks.collect_rss",
            "schedule": crontab(hour=22, minute=0),  # 每天 22:00
        },
        "collect-platforms-daily": {
            "task": "src.worker.tasks.collect_platforms",
            "schedule": crontab(hour=22, minute=30),
        },
    },
)
```

### 2.6.2 任务定义

```python
# src/worker/tasks.py
import asyncio
from src.worker.celery_app import celery_app
from src.collector.rss_collector import RSSCollector
from src.collector.tianapi_collector import TianAPICollector
from src.collector.dedup import deduplicate_content
from src.db.database import get_db
from src.models.content import Content

@celery_app.task
def collect_rss():
    collector = RSSCollector()
    items = collector.collect()
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}

@celery_app.task
def collect_platforms():
    collector = TianAPICollector()
    items = asyncio.run(collector.collect(["weibo", "douyin", "baidu"]))
    items = deduplicate_content(items)
    _save_contents(items)
    return {"collected": len(items)}

def _save_contents(items: List[Dict]):
    for item in items:
        with get_db() as db:
            try:
                existing = db.query(Content).filter_by(content_id=item["content_id"]).first()
                if not existing:
                    content = Content(**item)
                    db.add(content)
                    db.commit()
            except Exception as e:
                db.rollback()
```

---

## 2.7 验收标准

| 检查项 | 标准 |
|--------|------|
| RSS 采集 | 成功解析至少 3 个 RSS 源 |
| 微博热搜 | TianAPI weibohot 返回 ≥ 40 条 |
| 抖音热搜 | TianAPI douyinhot 返回 ≥ 40 条 |
| 百度热搜 | TianAPI networkhot 返回 ≥ 30 条 |
| 去重 | 相同 content_id 内容不重复入库 |
| Celery Beat | 定时任务按时触发 |
| 错误处理 | 单个源失败不影响整体采集 |
| 测试 | 单元测试通过 |

---

## 2.8 依赖关系

```
Phase 1 ──→ Phase 2
              │
              ├─→ config.py (bing_api_key 可选)
              ├─→ models/content.py (数据存储)
              ├─→ db/database.py (会话管理)
              └─→ Redis（Celery broker，已在 Phase 1）
                          │
                          ↓
                    Phase 3 (Embedding)
```

---

## 2.9 新增依赖

```
feedparser>=5.3.0       # RSS 解析
httpx>=0.27.0           # 异步 HTTP 客户端
beautifulsoup4>=4.12.0  # DuckDuckGo HTML 解析
celery>=5.3.0           # 任务队列
```

**TianAPI**：注册免费获取 Key，100 次/天额度，无强制付费。
