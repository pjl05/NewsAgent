from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCollector(ABC):
    """采集器抽象基类"""

    @abstractmethod
    def collect(self, sources: List[str] | None = None) -> List[Dict[str, Any]]:
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
