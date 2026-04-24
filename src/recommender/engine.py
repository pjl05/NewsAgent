"""Recommendation engine for personalized content ranking."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import desc

from src.db.database import get_db
from src.models.content import Content
from src.recommender.collab import CollaborativeFilter
from src.recommender.scorer import calculate_score
from src.recommender.user_embedder import UserEmbedder

logger = logging.getLogger(__name__)

# Default embedding dimension for fallback zero vector
DEFAULT_EMBEDDING_DIM = 128


class RecommendationEngine:
    """Personalized recommendation engine.

    Ranks content items based on:
    - Content-user cosine similarity (via embeddings)
    - Collaborative filter score
    - Freshness decay
    - Interaction boost (like_count)

    Weights (initial config from design doc section 3.2.2):
        alpha = 0.5 (content-user similarity)
        beta  = 0.2 (collaborative filter)
        gamma = 0.2 (freshness)
        delta = 0.1 (interaction boost)
    """

    def __init__(self, collab_filter: CollaborativeFilter) -> None:
        """Initialize the recommendation engine.

        Args:
            collab_filter: CollaborativeFilter instance for collab-based scoring
        """
        self.collab = collab_filter
        self.user_embedder = UserEmbedder()
        # Scoring weights from design doc section 3.2.2
        self.alpha = 0.5
        self.beta = 0.2
        self.gamma = 0.2
        self.delta = 0.1

    def rank(
        self,
        user_id: Optional[str],
        contents: List[Dict[str, Any]],
        top_k: int = 20,
    ) -> List[Dict[str, Any]]:
        """Rank content list by personalized score for a given user.

        Args:
            user_id: User identifier (optional, skips collab scoring if None)
            contents: List of content dicts with keys:
                - published_at: datetime
                - like_count: int
                - content_id: str
                - embedding: List[float] or None
            top_k: Maximum number of results to return (default 20)

        Returns:
            Top-k content items sorted by score in descending order
        """
        # Build user embedding from interactions
        user_embedding: Optional[List[float]] = None
        if user_id:
            try:
                user_embedding = asyncio.run(
                    self.user_embedder.build_from_interactions(user_id)
                )
                if user_embedding is None:
                    logger.warning(
                        "[RecommendationEngine] Could not build user embedding for user_id=%s",
                        user_id,
                    )
            except Exception as e:
                logger.error(
                    "[RecommendationEngine] Error building user embedding for user_id=%s: %s",
                    user_id,
                    e,
                )

        # Fallback to zero vector if no user embedding
        if user_embedding is None:
            user_embedding = [0.0] * DEFAULT_EMBEDDING_DIM

        # Load collab data for user if user_id provided
        if user_id:
            try:
                self.collab.load_from_db(user_id)
            except Exception as e:
                logger.warning(
                    "[RecommendationEngine] Could not load collab data for user_id=%s: %s",
                    user_id,
                    e,
                )

        now = datetime.utcnow()
        scored_contents: List[tuple[float, Dict[str, Any]]] = []

        for content in contents:
            published_at = content.get("published_at", now)
            age_days = max(0, (now - published_at).days)
            # Linear freshness decay per design doc 3.3.5
            freshness = max(0.0, 1.0 - (age_days * 0.1))
            like_count = content.get("like_count", 0)
            interaction_boost = min(1.0, like_count / 100.0)

            collab_score = 0.0
            if user_id:
                content_id = content.get("content_id")
                if content_id:
                    collab_score = self.collab.predict(user_id, content_id)

            embedding = content.get("embedding")
            if embedding is None:
                embedding = [0.0] * DEFAULT_EMBEDDING_DIM

            score = calculate_score(
                user_embedding=user_embedding,
                content_embedding=embedding,
                collab_score=collab_score,
                freshness=freshness,
                interaction_boost=interaction_boost,
                alpha=self.alpha,
                beta=self.beta,
                gamma=self.gamma,
                delta=self.delta,
            )
            scored_contents.append((score, content))

        scored_contents.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scored_contents[:top_k]]

    def get_recommendations(
        self,
        user_id: str,
        top_k: int = 20,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user.

        Loads recent content from database, ranks them, and returns top-k.

        Args:
            user_id: User identifier
            top_k: Maximum number of recommendations to return (default 20)
            limit: Maximum number of content items to fetch from DB (default 100)

        Returns:
            List of top-k recommended content dicts
        """
        contents: List[Dict[str, Any]] = []

        try:
            with get_db() as db:
                db_contents = (
                    db.query(Content)
                    .order_by(desc(Content.published_at))
                    .limit(limit)
                    .all()
                )

                for c in db_contents:
                    contents.append(
                        {
                            "content_id": c.content_id,
                            "title": c.title,
                            "source": c.source,
                            "url": c.url,
                            "published_at": c.published_at,
                            "summary": c.summary,
                            "tags": c.tags or [],
                            "embedding": c.embedding,
                            "like_count": c.like_count or 0,
                        }
                    )

                logger.info(
                    "[RecommendationEngine] Loaded %d content items for recommendations",
                    len(contents),
                )

        except Exception as e:
            logger.error(
                "[RecommendationEngine] Failed to load content from DB: %s",
                e,
            )
            return []

        if not contents:
            logger.info(
                "[RecommendationEngine] No content available for user_id=%s",
                user_id,
            )
            return []

        return self.rank(user_id=user_id, contents=contents, top_k=top_k)
