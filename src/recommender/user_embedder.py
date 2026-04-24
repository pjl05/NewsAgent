from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from src.models.interaction import Interaction
from src.db.database import get_db
from src.recommender.embedder import ContentEmbedder

logger = logging.getLogger(__name__)


class UserEmbedder:
    """用户兴趣向量构建器

    从用户的订阅主题和交互历史构建用户兴趣向量。
    策略：
    1. 收集用户交互过的内容的标签
    2. 用 Embedder 生成每个标签的向量
    3. 加权平均得到用户兴趣向量
    """

    def __init__(self) -> None:
        self.embedder = ContentEmbedder()
        self.action_weights = {
            "read": 0.3,
            "like": 0.6,
            "share": 0.9,
            "click": 0.4,
        }
        self.default_weight = 0.5

    def _normalize_text(self, text: str) -> str:
        import re
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _get_weight(self, action: str) -> float:
        return self.action_weights.get(action.lower(), self.default_weight)

    async def build_from_interactions(
        self,
        user_id: str,
        max_contents: int = 50,
    ) -> Optional[List[float]]:
        with get_db() as db:
            interactions = (
                db.query(Interaction)
                .filter_by(user_id=user_id)
                .order_by(Interaction.created_at.desc())
                .limit(max_contents)
                .all()
            )

        if not interactions:
            logger.info("[UserEmbedder] No interactions for user %s", user_id)
            return None

        tag_weights: Dict[str, float] = {}
        for i in interactions:
            weight = self._get_weight(i.action) * (i.weight or 1.0)
            parts = i.content_id.split("_")
            tag = parts[0] if parts else "general"
            tag_weights[tag] = tag_weights.get(tag, 0.0) + weight

        if not tag_weights:
            return None

        embeddings: List[List[float]] = []
        weights: List[float] = []

        for tag, weight in tag_weights.items():
            text = self._normalize_text(tag)
            if not text:
                continue
            try:
                emb = await self.embedder.embed_text(text)
                embeddings.append(emb)
                weights.append(weight)
            except Exception as e:
                logger.warning("[UserEmbedder] Failed to embed tag '%s': %s", tag, e)
                continue

        if not embeddings:
            return None

        import numpy as np

        embeddings_arr = np.array(embeddings)
        weights_arr = np.array(weights)
        weight_sum = weights_arr.sum()
        if weight_sum == 0:
            return None

        user_vector = (embeddings_arr * weights_arr.reshape(-1, 1)).sum(axis=0) / weight_sum
        return user_vector.tolist()

    async def build_from_topics(
        self,
        topics: List[str],
        weights: Optional[List[float]] = None,
    ) -> Optional[List[float]]:
        if not topics:
            return None

        weights = weights or [1.0] * len(topics)

        embeddings: List[List[float]] = []
        weight_list: List[float] = []

        for topic, weight in zip(topics, weights):
            text = self._normalize_text(topic)
            if not text:
                continue
            try:
                emb = await self.embedder.embed_text(text)
                embeddings.append(emb)
                weight_list.append(weight)
            except Exception as e:
                logger.warning("[UserEmbedder] Failed to embed topic '%s': %s", topic, e)
                continue

        if not embeddings:
            return None

        import numpy as np

        embeddings_arr = np.array(embeddings)
        weights_arr = np.array(weight_list)
        weight_sum = weights_arr.sum()
        if weight_sum == 0:
            return None

        user_vector = (embeddings_arr * weights_arr.reshape(-1, 1)).sum(axis=0) / weight_sum
        return user_vector.tolist()
