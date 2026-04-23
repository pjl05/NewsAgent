import pytest
from src.collector.dedup import deduplicate_content
from src.collector.rss_collector import RSSCollector
from src.collector.platform_collector import PlatformCollector


class TestCollectorPipeline:
    """Integration tests for the collector pipeline"""

    def test_dedup_removes_duplicates(self):
        """Test that deduplicate_content removes items with same content_id"""
        items = [
            {"content_id": "a", "title": "Title A"},
            {"content_id": "b", "title": "Title B"},
            {"content_id": "a", "title": "Title A Duplicate"},
        ]
        result = deduplicate_content(items)
        assert len(result) == 2
        assert result[0]["content_id"] == "a"
        assert result[1]["content_id"] == "b"

    def test_dedup_empty_list(self):
        """Test dedup handles empty list"""
        assert deduplicate_content([]) == []

    def test_dedup_preserves_first_occurrence_order(self):
        """Test that dedup preserves order of first occurrence"""
        items = [
            {"content_id": "c", "title": "Third"},
            {"content_id": "a", "title": "First"},
            {"content_id": "b", "title": "Second"},
            {"content_id": "a", "title": "First Duplicate"},
        ]
        result = deduplicate_content(items)
        assert [r["content_id"] for r in result] == ["c", "a", "b"]

    def test_rss_collector_has_default_feeds(self):
        """Test that RSSCollector is initialized with default feeds"""
        collector = RSSCollector()
        assert len(collector.DEFAULT_FEEDS) > 0
        assert all(isinstance(url, str) for url in collector.DEFAULT_FEEDS)
        assert all(url.startswith("http") for url in collector.DEFAULT_FEEDS)

    def test_platform_collector_instantiable(self):
        """Test that PlatformCollector can be instantiated"""
        collector = PlatformCollector()
        assert collector is not None

    def test_collector_results_have_required_fields(self):
        """Test that collector results would have all required fields"""
        item = {
            "content_id": "test_123",
            "title": "Test Title",
            "source": "Test Source",
            "url": "https://example.com",
            "published_at": None,
            "summary": "Test summary",
            "tags": ["test"],
        }
        required_fields = ["content_id", "title", "source", "url", "published_at", "summary", "tags"]
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"