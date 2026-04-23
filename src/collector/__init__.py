from .base import BaseCollector
from .rss_collector import RSSCollector
from .search_collector import SearchCollector
from .platform_collector import PlatformCollector
from .dedup import deduplicate_content

__all__ = [
    "BaseCollector",
    "RSSCollector",
    "SearchCollector",
    "PlatformCollector",
    "deduplicate_content",
]