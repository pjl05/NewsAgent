from __future__ import annotations

import pytest
from datetime import datetime, timezone
from src.recommender.scorer import cosine_similarity, freshness_decay, calculate_score


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_opposite_vectors(self):
        assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_zero_vector(self):
        assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

    def test_multidimensional(self):
        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]
        result = cosine_similarity(a, b)
        assert -1.0 <= result <= 1.0

    def test_returns_float(self):
        assert isinstance(cosine_similarity([1, 0], [1, 0]), float)


class TestFreshnessDecay:
    def test_fresh_content(self):
        now = datetime.now(timezone.utc)
        assert freshness_decay(now) == pytest.approx(1.0)

    def test_one_day_old(self):
        from datetime import timedelta
        old = datetime.now(timezone.utc) - timedelta(days=1)
        score = freshness_decay(old, half_life_days=7.0)
        assert 0.5 < score < 1.0

    def test_old_content_near_zero(self):
        from datetime import timedelta
        old = datetime.now(timezone.utc) - timedelta(days=30)
        score = freshness_decay(old, half_life_days=7.0)
        assert score >= 0.0
        assert score < 0.1


class TestCalculateScore:
    def test_returns_float(self):
        result = calculate_score(
            user_embedding=[1.0, 0.0],
            content_embedding=[1.0, 0.0],
            collab_score=0.0,
            freshness=1.0,
            interaction_boost=0.0,
        )
        assert isinstance(result, float)

    def test_within_range(self):
        for _ in range(10):
            result = calculate_score(
                user_embedding=[1.0, 0.5],
                content_embedding=[0.8, 0.3],
                collab_score=0.5,
                freshness=0.8,
                interaction_boost=0.3,
            )
            assert 0.0 <= result <= 1.0

    def test_all_zeros(self):
        result = calculate_score(
            user_embedding=[0.0, 0.0],
            content_embedding=[0.0, 0.0],
            collab_score=0.0,
            freshness=0.0,
            interaction_boost=0.0,
        )
        assert result == 0.0

    def test_custom_weights(self):
        result = calculate_score(
            user_embedding=[1.0, 0.0],
            content_embedding=[1.0, 0.0],
            collab_score=0.0,
            freshness=1.0,
            interaction_boost=0.0,
            alpha=1.0, beta=0.0, gamma=0.0, delta=0.0,
        )
        assert result == pytest.approx(1.0)
