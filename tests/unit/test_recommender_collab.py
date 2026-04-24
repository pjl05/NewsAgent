from __future__ import annotations

import pytest
from src.recommender.collab import CollaborativeFilter


class TestCollaborativeFilter:
    def test_add_interaction(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        assert "user1" in cf.user_item_matrix
        assert cf.user_item_matrix["user1"]["content1"] == 1.0

    def test_add_multiple_interactions(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        cf.add_interaction("user1", "content2", 0.5)
        assert len(cf.user_item_matrix["user1"]) == 2

    def test_get_similar_users_no_interactions(self):
        cf = CollaborativeFilter()
        result = cf.get_similar_users("nonexistent_user")
        assert result == []

    def test_get_similar_users_identical(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        cf.add_interaction("user1", "content2", 1.0)
        cf.add_interaction("user2", "content1", 1.0)
        cf.add_interaction("user2", "content2", 1.0)
        similar = cf.get_similar_users("user1", top_k=5)
        user_ids = [u for u, _ in similar]
        assert "user2" in user_ids
        sim_score = next(s for u, s in similar if u == "user2")
        assert sim_score == 1.0

    def test_get_similar_users_no_overlap(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        cf.add_interaction("user2", "content2", 1.0)
        # No shared content → Jaccard = 0 → not added to similar users
        similar = cf.get_similar_users("user1", top_k=5)
        user_ids = [u for u, _ in similar]
        assert "user2" not in user_ids

    def test_predict_no_similar_users(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        result = cf.predict("user1", "content999")
        assert result == 0.0

    def test_predict_with_similar_users(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        cf.add_interaction("user2", "content1", 0.8)
        result = cf.predict("user1", "content1")
        # user2 is similar (Jaccard=1.0) and rated content1 as 0.8
        assert result == 0.8

    def test_predict_returns_zero_for_unknown_content(self):
        cf = CollaborativeFilter()
        cf.add_interaction("user1", "content1", 1.0)
        result = cf.predict("user1", "never_seen_content")
        assert result == 0.0

    def test_top_k_limits_results(self):
        cf = CollaborativeFilter()
        for i in range(10):
            cf.add_interaction(f"user{i}", "content_shared", 1.0)
        cf.add_interaction("user0", "content_shared", 1.0)
        similar = cf.get_similar_users("user0", top_k=3)
        assert len(similar) <= 3
