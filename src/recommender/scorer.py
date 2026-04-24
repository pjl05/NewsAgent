"""Scoring utilities for the recommendation engine."""

import numpy as np
from datetime import datetime, timezone
from typing import List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        a: First vector
        b: Second vector

    Returns:
        Cosine similarity score between 0.0 and 1.0
    """
    a = np.array(a)
    b = np.array(b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def freshness_decay(published_at: datetime, half_life_days: float = 7.0) -> float:
    """Calculate freshness score that decays by half every half_life_days.

    The score starts at 1.0 for new content and decays exponentially,
    reaching 0.5 after half_life_days.

    Args:
        published_at: Publication datetime of the content
        half_life_days: Number of days for the score to decay to 0.5 (default 7.0)

    Returns:
        Freshness score between 0.0 and 1.0
    """
    now = datetime.now(timezone.utc)
    age_days = max(0.0, (now - published_at).total_seconds() / 86400.0)
    decay_rate = np.log(2) / half_life_days
    freshness = np.exp(-decay_rate * age_days)
    return float(np.clip(freshness, 0.0, 1.0))


def calculate_score(
    user_embedding: List[float],
    content_embedding: List[float],
    collab_score: float,
    freshness: float,
    interaction_boost: float,
    alpha: float = 0.5,
    beta: float = 0.2,
    gamma: float = 0.2,
    delta: float = 0.1,
) -> float:
    """Calculate personalized content score.

    Score formula:
        score = alpha * cosine_similarity(user_emb, content_emb)
              + beta * collab_score
              + gamma * freshness
              + delta * interaction_boost

    Args:
        user_embedding: User interest vector
        content_embedding: Content embedding vector
        collab_score: Collaborative filter score
        freshness: Freshness decay score (0.0 to 1.0)
        interaction_boost: Interaction signal boost (0.0 to 1.0)
        alpha: Weight for content-user similarity (default 0.5)
        beta: Weight for collaborative filter (default 0.2)
        gamma: Weight for freshness (default 0.2)
        delta: Weight for interaction boost (default 0.1)

    Returns:
        Normalized score between 0.0 and 1.0
    """
    similarity = cosine_similarity(user_embedding, content_embedding)
    score = (
        alpha * similarity
        + beta * collab_score
        + gamma * freshness
        + delta * interaction_boost
    )
    return float(np.clip(score, 0.0, 1.0))
