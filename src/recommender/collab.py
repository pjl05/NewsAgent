"""Collaborative filtering for user-based recommendations."""

import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select

from src.db.database import get_db
from src.models.interaction import Interaction

logger = logging.getLogger(__name__)


class CollaborativeFilter:
    """基于用户行为的协同过滤推荐 (User-Based Collaborative Filtering).

    使用 Jaccard 相似度计算用户之间的相似性，基于共同交互的内容项目。
    """

    def __init__(self) -> None:
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)

    def add_interaction(self, user_id: str, content_id: str, weight: float) -> None:
        """添加用户交互记录到矩阵中。

        Args:
            user_id: 用户标识符
            content_id: 内容标识符
            weight: 交互权重 (0.0-1.0)
        """
        self.user_item_matrix[user_id][content_id] = weight
        logger.debug(
            "Added interaction: user_id=%s, content_id=%s, weight=%.2f",
            user_id,
            content_id,
            weight,
        )

    def get_similar_users(
        self, user_id: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """查找与目标用户相似的用户 (Jaccard 相似度).

        Jaccard = |A ∩ B| / |A ∪ B|，基于用户共同交互的内容项目集合。

        Args:
            user_id: 目标用户 ID
            top_k: 返回的相似用户数量上限

        Returns:
            按相似度降序排列的 [(user_id, similarity_score), ...] 列表
        """
        if user_id not in self.user_item_matrix:
            logger.debug("User %s not found in matrix, returning empty list", user_id)
            return []

        target_items = self.user_item_matrix[user_id]
        similarities: List[Tuple[str, float]] = []

        for other_user, items in self.user_item_matrix.items():
            if other_user == user_id:
                continue

            intersection = set(target_items.keys()) & set(items.keys())
            union = set(target_items.keys()) | set(items.keys())

            if intersection:
                sim = len(intersection) / len(union)
                similarities.append((other_user, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        result = similarities[:top_k]

        logger.debug(
            "Found %d similar users for user_id=%s (top_k=%d)",
            len(result),
            user_id,
            top_k,
        )
        return result

    def predict(self, user_id: str, content_id: str) -> float:
        """预测用户对内容的评分 (加权平均相似度).

        基于相似用户的评分，使用相似度作为权重进行加权平均。

        Args:
            user_id: 用户 ID
            content_id: 内容 ID

        Returns:
            预测评分 (0.0-1.0)，无可用相似用户时返回 0.0
        """
        similar_users = self.get_similar_users(user_id)
        if not similar_users:
            logger.debug(
                "No similar users found for user_id=%s, content_id=%s, returning 0.0",
                user_id,
                content_id,
            )
            return 0.0

        numerator = 0.0
        denominator = 0.0

        for other_user, sim in similar_users:
            if content_id in self.user_item_matrix[other_user]:
                rating = self.user_item_matrix[other_user][content_id]
                numerator += sim * rating
                denominator += sim

        if denominator == 0:
            return 0.0

        predicted = numerator / denominator
        logger.debug(
            "Predicted score for user_id=%s, content_id=%s: %.4f",
            user_id,
            content_id,
            predicted,
        )
        return predicted

    def load_from_db(self, user_id: str) -> int:
        """从 PostgreSQL Interaction 表加载用户的历史交互记录。

        将数据库中的交互记录填充到 user_item_matrix 中。
        默认使用 Interaction.weight 字段作为权重。

        Args:
            user_id: 要加载的用户 ID

        Returns:
            加载的交互记录数量
        """
        count = 0
        try:
            with get_db() as db:
                stmt = select(Interaction).where(Interaction.user_id == user_id)
                interactions = db.execute(stmt).scalars().all()

                for interaction in interactions:
                    self.add_interaction(
                        user_id=interaction.user_id,
                        content_id=interaction.content_id,
                        weight=interaction.weight if interaction.weight is not None else 0.0,
                    )
                    count += 1

                logger.info(
                    "Loaded %d interactions from DB for user_id=%s",
                    count,
                    user_id,
                )
        except Exception as e:
            logger.error(
                "Failed to load interactions from DB for user_id=%s: %s",
                user_id,
                e,
            )
            raise

        return count