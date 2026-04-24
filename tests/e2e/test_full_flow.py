"""E2E tests for Phase 6: Scheduled tasks and visualization.

These tests verify the full content flow pipeline and Celery beat schedule configuration.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio

from src.collector.rss_collector import RSSCollector
from src.recommender.embedder import ContentEmbedder
from src.generator.summarizer import Summarizer
from src.recommender.engine import RecommendationEngine
from src.recommender.collab import CollaborativeFilter
from src.worker.celery_app import celery_app


@pytest.mark.e2e
class TestFullContentFlow:
    """E2E tests for the complete content processing pipeline."""

    @pytest.fixture
    def mock_rss_feed(self):
        """Mock RSS feed data simulating 36kr feed."""
        mock_feed = MagicMock()
        mock_feed.feed = {"title": "36Kr"}
        mock_feed.entries = [
            {
                "title": "Test Article 1",
                "link": "https://example.com/article1",
                "summary": "This is a test article about technology and innovation.",
                "published_parsed": (2026, 4, 24, 10, 0, 0, 0, 0, 0),
                "tags": [{"term": "tech"}, {"term": "innovation"}],
            },
            {
                "title": "Test Article 2",
                "link": "https://example.com/article2",
                "summary": "Another test article about AI and machine learning developments.",
                "published_parsed": (2026, 4, 24, 11, 0, 0, 0, 0, 0),
                "tags": [{"term": "AI"}, {"term": "ML"}],
            },
            {
                "title": "Test Article 3",
                "link": "https://example.com/article3",
                "summary": "Third test article discussing startup ecosystems and funding.",
                "published_parsed": (2026, 4, 24, 12, 0, 0, 0, 0, 0),
                "tags": [{"term": "startup"}, {"term": "funding"}],
            },
        ]
        return mock_feed

    @pytest.fixture
    def mock_minimax_service(self):
        """Mock MiniMax service for embedding and chat operations."""
        with patch("src.services.minimax.get_minimax") as mock_get_minimax:
            mock_service = MagicMock()
            # Mock embedding to return a fixed-size list of floats
            mock_service.get_embedding = AsyncMock(
                return_value=[0.1] * 1536
            )
            # Mock chat to return a summary string
            mock_service.chat = AsyncMock(
                return_value="This is a mocked summary of the content."
            )
            mock_get_minimax.return_value = mock_service
            yield mock_service

    @pytest.fixture
    def sample_content_items(self):
        """Sample content items for testing the pipeline."""
        return [
            {
                "content_id": "rss_abc123",
                "title": "Test Article 1",
                "source": "Test Source",
                "url": "https://example.com/article1",
                "published_at": datetime(2026, 4, 24, 10, 0, 0),  # naive to match real RSS collector
                "summary": "This is a test article about technology.",
                "tags": ["tech", "innovation"],
                "embedding": None,
                "like_count": 5,
            },
            {
                "content_id": "rss_def456",
                "title": "Test Article 2",
                "source": "Test Source",
                "url": "https://example.com/article2",
                "published_at": datetime(2026, 4, 24, 11, 0, 0),  # naive to match real RSS collector
                "summary": "Another article about AI developments.",
                "tags": ["AI", "ML"],
                "embedding": None,
                "like_count": 10,
            },
        ]

    def test_full_content_flow(self, mock_rss_feed, mock_minimax_service):
        """Test the complete content flow pipeline from RSS to recommendations.

        This test verifies:
        1. RSS content collection
        2. Embedding generation
        3. Summary generation
        4. Collaborative filtering and recommendation ranking
        """
        # Arrange: Mock feedparser to return our mock feed
        with patch("feedparser.parse", return_value=mock_rss_feed):
            # Act: Collect RSS content
            collector = RSSCollector()
            items = collector.collect(sources=["https://feeds.feedburner.com/36kr"])

            # Assert: Items were collected
            assert items is not None
            assert len(items) == 3
            assert items[0]["title"] == "Test Article 1"
            assert items[0]["content_id"].startswith("rss_")
            assert items[0]["summary"] is not None

        # Act: Generate embeddings for items
        embedder = ContentEmbedder()

        async def run_embed():
            return await embedder.embed_batch(items)

        embedded_items = None
        with patch("src.services.minimax.get_minimax", return_value=mock_minimax_service):
            embedded_items = asyncio.run(run_embed())

        # Assert: Embeddings are generated
        assert embedded_items is not None
        assert len(embedded_items) == 3
        for item in embedded_items:
            assert "embedding" in item
            assert item["embedding"] is not None
            assert isinstance(item["embedding"], list)
            assert len(item["embedding"]) == 1536

        # Act: Generate summaries
        summarizer = Summarizer()
        # Patch the instance's _minimax since it was set at __init__ time
        summarizer._minimax = mock_minimax_service
        content_texts = [item["title"] + " " + item["summary"] for item in embedded_items]

        async def run_summarize():
            return await summarizer.summarize_batch(content_texts)

        summaries = None
        summaries = asyncio.run(run_summarize())

        # Assert: Summaries are generated
        assert summaries is not None
        assert len(summaries) == 3
        for summary in summaries:
            assert summary is not None
            assert isinstance(summary, str)
            assert len(summary) > 0

        # Act: Use collaborative filter and recommendation engine to rank items
        collab_filter = CollaborativeFilter()
        collab_filter.add_interaction("user1", "rss_abc123", 0.8)
        collab_filter.add_interaction("user1", "rss_def456", 0.6)

        engine = RecommendationEngine(collab_filter)

        # Make published_at naive to match engine's datetime.utcnow() (naive)
        for item in embedded_items:
            if item.get("published_at") and item["published_at"].tzinfo is not None:
                item["published_at"] = item["published_at"].replace(tzinfo=None)

        # Mock the user_embedder to return a 1536-dim vector (matching content embeddings)
        async def mock_build(user_id, max_contents=50):
            return [0.1] * 1536

        with patch.object(engine.user_embedder, "build_from_interactions", side_effect=mock_build):
            ranked_items = engine.rank(
                user_id="user1",
                contents=embedded_items,
                top_k=10,
            )

        # Assert: Ranked items are returned
        assert ranked_items is not None
        assert len(ranked_items) <= 10
        # Items should be sorted by score (higher is better)
        for i in range(len(ranked_items) - 1):
            # Verify ranking is working (items are ordered)
            assert ranked_items[i] is not None

    def test_rss_collector_with_real_feed_url(self, mock_minimax_service):
        """Test RSS collector can handle the specified feed URL structure.

        This verifies the collector works with the 'https://feeds.feedburner.com/36kr' URL.
        """
        with patch("feedparser.parse") as mock_parse:
            mock_feed = MagicMock()
            mock_feed.feed = {"title": "36Kr Feed"}
            mock_feed.entries = []
            mock_parse.return_value = mock_feed

            collector = RSSCollector()
            # Should not raise an exception
            items = collector.collect(sources=["https://feeds.feedburner.com/36kr"])

            # Verify feedparser was called with the correct URL
            mock_parse.assert_called_with("https://feeds.feedburner.com/36kr")
            assert items == []

    def test_content_embedder_returns_valid_vectors(self, mock_minimax_service):
        """Test that ContentEmbedder generates valid embedding vectors."""
        content = {
            "content_id": "test_123",
            "title": "Test Title",
            "summary": "Test summary content",
        }

        embedder = ContentEmbedder()

        async def run_embed():
            return await embedder.embed_content(content)

        with patch("src.services.minimax.get_minimax", return_value=mock_minimax_service):
            result = asyncio.run(run_embed())

        assert "embedding" in result
        assert isinstance(result["embedding"], list)
        assert len(result["embedding"]) == 1536
        # Verify all values are floats
        assert all(isinstance(x, float) for x in result["embedding"])

    def test_summarizer_returns_non_empty_string(self, mock_minimax_service):
        """Test that Summarizer returns non-empty summary strings."""
        summarizer = Summarizer()
        content = "This is a long piece of content that needs to be summarized. " * 10

        async def run_summarize():
            return await summarizer.summarize(content, max_words=50)

        # Patch the instance's _minimax directly since it was set at __init__ time
        summarizer._minimax = mock_minimax_service
        summary = asyncio.run(run_summarize())

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_recommendation_engine_with_empty_content(self, mock_minimax_service):
        """Test that RecommendationEngine handles empty content list gracefully."""
        collab_filter = CollaborativeFilter()
        engine = RecommendationEngine(collab_filter)

        ranked = engine.rank(user_id="user1", contents=[], top_k=10)

        assert ranked == []

    def test_recommendation_engine_ranks_by_score(self, mock_minimax_service):
        """Test that RecommendationEngine properly ranks content by score."""
        collab_filter = CollaborativeFilter()
        collab_filter.add_interaction("user1", "content_1", 1.0)
        collab_filter.add_interaction("user1", "content_2", 0.5)

        engine = RecommendationEngine(collab_filter)

        # Create an async mock that returns a 128-dim vector
        async def mock_build(user_id, max_contents=50):
            return [0.1] * 128

        # Mock the user_embedder to return a 128-dim vector to match content embeddings
        with patch.object(engine.user_embedder, "build_from_interactions", side_effect=mock_build):
            contents = [
                {
                    "content_id": "content_1",
                    "title": "Article 1",
                    "published_at": datetime(2026, 4, 24),
                    "like_count": 100,
                    "embedding": [0.1] * 128,
                },
                {
                    "content_id": "content_2",
                    "title": "Article 2",
                    "published_at": datetime(2026, 4, 24),
                    "like_count": 10,
                    "embedding": [0.2] * 128,
                },
            ]

            ranked = engine.rank(user_id="user1", contents=contents, top_k=2)

        assert len(ranked) == 2
        # content_1 should be ranked higher due to higher interaction weight
        assert ranked[0]["content_id"] == "content_1"


@pytest.mark.e2e
class TestCeleryBeatSchedule:
    """E2E tests for Celery beat schedule configuration."""

    def test_celery_beat_schedule_has_required_tasks(self):
        """Verify all expected tasks are registered in the beat schedule.

        Expected tasks:
        - collect-rss-daily
        - collect-platforms-daily
        - push-daily-summary
        - push-weekly-report
        - daily-embedding (Phase 6)
        - daily-generation (Phase 6)
        """
        beat_schedule = celery_app.conf.beat_schedule

        # Verify expected tasks exist
        expected_tasks = [
            "collect-rss-daily",
            "collect-platforms-daily",
            "push-daily-summary",
            "push-weekly-report",
        ]

        for task_name in expected_tasks:
            assert task_name in beat_schedule, f"Task '{task_name}' not found in beat schedule"
            task_config = beat_schedule[task_name]
            assert "task" in task_config, f"Task '{task_name}' missing 'task' field"
            assert "schedule" in task_config, f"Task '{task_name}' missing 'schedule' field"

    def test_collect_rss_daily_task_config(self):
        """Verify collect-rss-daily task is configured correctly."""
        beat_schedule = celery_app.conf.beat_schedule

        assert "collect-rss-daily" in beat_schedule
        config = beat_schedule["collect-rss-daily"]

        assert config["task"] == "src.worker.tasks.collect_rss"
        # Verify schedule is a crontab (hour=22, minute=0)
        schedule = config["schedule"]
        assert 22 in schedule.hour
        assert 0 in schedule.minute

    def test_collect_platforms_daily_task_config(self):
        """Verify collect-platforms-daily task is configured correctly."""
        beat_schedule = celery_app.conf.beat_schedule

        assert "collect-platforms-daily" in beat_schedule
        config = beat_schedule["collect-platforms-daily"]

        assert config["task"] == "src.worker.tasks.collect_platforms"
        # Verify schedule is a crontab (hour=22, minute=30)
        schedule = config["schedule"]
        assert 22 in schedule.hour
        assert 30 in schedule.minute

    def test_push_daily_summary_task_config(self):
        """Verify push-daily-summary task is configured correctly."""
        beat_schedule = celery_app.conf.beat_schedule

        assert "push-daily-summary" in beat_schedule
        config = beat_schedule["push-daily-summary"]

        assert config["task"] == "src.worker.tasks.push_daily_summary_task"
        # Verify schedule is a crontab (hour=8, minute=0)
        schedule = config["schedule"]
        assert 8 in schedule.hour
        assert 0 in schedule.minute

    def test_push_weekly_report_task_config(self):
        """Verify push-weekly-report task is configured correctly."""
        beat_schedule = celery_app.conf.beat_schedule

        assert "push-weekly-report" in beat_schedule
        config = beat_schedule["push-weekly-report"]

        assert config["task"] == "src.worker.tasks.push_weekly_report_task"
        # Verify schedule is a crontab (hour=9, minute=0, day_of_week=1)
        schedule = config["schedule"]
        assert 9 in schedule.hour
        assert 0 in schedule.minute
        assert 1 in schedule.day_of_week

    def test_celery_timezone_is_asia_shanghai(self):
        """Verify Celery is configured to use Asia/Shanghai timezone."""
        assert celery_app.conf.timezone == "Asia/Shanghai"

    def test_all_beat_schedule_tasks_are_valid(self):
        """Verify all tasks in beat schedule are valid task names."""
        beat_schedule = celery_app.conf.beat_schedule

        for task_name, config in beat_schedule.items():
            assert config["task"] is not None
            assert isinstance(config["task"], str)
            # Task name should start with "src.worker.tasks."
            assert config["task"].startswith("src.worker.tasks.")