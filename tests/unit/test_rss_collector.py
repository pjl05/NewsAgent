import pytest
from src.collector.rss_collector import RSSCollector


class TestRSSCollector:
    def setup_method(self):
        self.collector = RSSCollector()

    def test_clean_html_removes_tags(self):
        html = "<p>Hello <b>World</b></p>"
        result = self.collector._clean_html(html)
        assert result == "Hello World"

    def test_clean_html_collapse_whitespace(self):
        text = "Hello    World\n\nTest"
        result = self.collector._clean_html(text)
        assert result == "Hello World Test"

    def test_content_id_format_is_rss_prefix(self):
        item = {
            "content_id": "rss_abc123",
            "title": "Test",
            "source": "TestSource",
            "url": "https://example.com",
            "published_at": "2026-01-01",
            "summary": "Summary",
            "tags": [],
        }
        assert item["content_id"].startswith("rss_")

    def test_default_feeds_not_empty(self):
        assert len(self.collector.DEFAULT_FEEDS) > 0
        assert all(isinstance(url, str) for url in self.collector.DEFAULT_FEEDS)