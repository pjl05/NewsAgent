# Phase 2: 内容采集

**阶段：** Phase 2
**工期：** 2 周
**前置依赖：** Phase 1

---

## 2.1 阶段目标

实现全网内容自动采集系统，包括：
1. RSS 订阅源采集（feedparser）
2. 搜索引擎采集（SerpAPI）
3. 垂直平台 API 采集（微博/知乎/雪球）

**交付物：** 自动化的内容采集管道，每日可采集数百条内容

---

## 2.2 技术架构

### 2.2.1 采集器架构

```
┌─────────────────────────────────────────────────────────────┐
│                    采集层 (Collector)                       │
├───────────────┬──────────────────┬──────────────────────────┤
│  RSSCollector │ SearchCollector │ PlatformCollector       │
│  (feedparser)│   (SerpAPI)      │   (Weibo/Zhihu/Xueqiu) │
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

### 2.2.2 数据采集流程

```
定时任务 (22:00)
     │
     ├─→ 1. RSS 采集
     │      ├─ 36kr RSS: https://36kr.com/feed
     │      ├─ 虎嗅 RSS: https://www.huxiu.com/rss/feed.xml
     │      ├─ 知乎 RSS: https://www.zhihu.com/rss
     │      └─ 更多 RSS 源...
     │
     ├─→ 2. 搜索采集
     │      ├─ AI 最新新闻 (SerpAPI)
     │      ├─ 科技股最新 (SerpAPI)
     │      └─ 用户订阅主题搜索
     │
     └─→ 3. 平台 API 采集
            ├─ 微博热搜榜
            ├─ 知乎热榜
            └─ 雪球话题
```

---

## 2.3 目录结构

```
src/collector/
├── __init__.py
├── base.py                  # 抽象基类
├── rss_collector.py         # RSS 采集
├── search_collector.py      # 搜索引擎采集
└── platform_collector.py     # 垂直平台采集
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

        Args:
            sources: 来源列表（如 URL 列表、关键词列表）

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

```python
import feedparser
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector

class RSSCollector(BaseCollector):
    """RSS/Atom 订阅源采集器"""

    def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        """解析 RSS/Atom 订阅源"""
        results = []
        for source in sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries:
                    item = self._parse_entry(entry, feed.feed, source)
                    if item:
                        results.append(item)
            except Exception as e:
                print(f"Error parsing {source}: {e}")
                continue
        return results

    def _parse_entry(self, entry, feed, source) -> Dict[str, Any]:
        """解析单条 RSS 条目"""
        link = entry.get("link", "")
        if not link:
            return None

        content_id = f"rss_{abs(hash(link))}"
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
        """解析发布日期"""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except:
                pass
        return datetime.utcnow()

    def _clean_html(self, text: str) -> str:
        """去除 HTML 标签"""
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_tags(self, entry) -> List[str]:
        """提取标签"""
        tags = []
        for tag in entry.get("tags", []):
            term = tag.get("term", "")
            if term:
                tags.append(term)
        return tags
```

### 2.4.3 SearchCollector

```python
import httpx
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector
from src.config import get_settings

settings = get_settings()

class SearchCollector(BaseCollector):
    """搜索引擎采集器 (SerpAPI)"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.serpapi_key
        self.base_url = "https://serpapi.com/search"

    def collect(self, queries: List[str]) -> List[Dict[str, Any]]:
        """根据关键词列表搜索采集内容"""
        results = []
        for query in queries:
            try:
                search_results = self._search(query)
                results.extend(search_results)
            except Exception as e:
                print(f"Error searching {query}: {e}")
                continue
        return results

    def _search(self, query: str) -> List[Dict[str, Any]]:
        """执行单次搜索"""
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 10,
        }

        with httpx.Client() as client:
            response = client.get(self.base_url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        results = []
        for r in data.get("organic_results", []):
            link = r.get("link", "")
            if not link:
                continue

            results.append({
                "content_id": f"search_{abs(hash(link))}",
                "title": r.get("title", ""),
                "source": r.get("source", ""),
                "url": link,
                "published_at": datetime.utcnow(),
                "summary": r.get("snippet", "")[:500],
                "tags": [query],
            })

        return results
```

### 2.4.4 PlatformCollector

```python
import httpx
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseCollector

class PlatformCollector(BaseCollector):
    """垂直平台内容采集器"""

    PLATFORMS = {
        "weibo": {"name": "微博", "hot_url": "https://api.weibo.com/1/trends/hot.json"},
        "zhihu": {"name": "知乎", "hot_url": "https://www.zhihu.com/api/v4/hot/replies/rank"},
        "xueqiu": {"name": "雪球", "hot_url": "https://stock.xueqiu.com/v1/stock/search.json"},
    }

    def collect(self, sources: List[str]) -> List[Dict[str, Any]]:
        """从指定平台采集热门内容"""
        results = []
        for source in sources:
            if source not in self.PLATFORMS:
                continue
            try:
                platform_data = self._fetch_platform(source)
                results.extend(platform_data)
            except Exception as e:
                print(f"Error fetching {source}: {e}")
                continue
        return results

    def _fetch_platform(self, platform: str) -> List[Dict[str, Any]]:
        """从单个平台获取热门内容"""
        return []
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

## 2.6 验收标准

| 检查项 | 标准 |
|--------|------|
| RSS 采集 | 能成功解析至少 3 个 RSS 源 |
| 搜索采集 | SerpAPI 返回结果正确解析 |
| 去重 | 相同 URL 内容不重复入库 |
| 错误处理 | 单个源失败不影响整体采集 |
| 测试 | 单元测试 100% 通过 |

---

## 2.7 依赖关系

```
Phase 1 ──→ Phase 2
              │
              ├─→ config.py (serpapi_key)
              ├─→ models/content.py (数据存储)
              └─→ db/database.py (会话管理)
                          │
                          ↓
                    Phase 3 (Embedding)
```
