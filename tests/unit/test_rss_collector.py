import pytest
from unittest.mock import MagicMock
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

    def test_parse_entry_returns_content_id_with_rss_prefix(self):
        """Test that _parse_entry generates content_id with rss_ prefix"""
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda k, d=None: {
            "link": "https://example.com/article",
            "title": "Test Title",
            "summary": "Test summary",
            "tags": [{"term": "AI"}, {"term": "Tech"}],
        }.get(k, d)
        mock_entry.published_parsed = None
        mock_feed = MagicMock()
        mock_feed.get.side_effect = lambda k, d=None: {"title": "Test Feed"}.get(k, d)

        result = self.collector._parse_entry(mock_entry, mock_feed, "https://example.com/feed")

        assert result is not None
        assert result["content_id"].startswith("rss_")
        assert result["title"] == "Test Title"
        assert result["source"] == "Test Feed"
        assert result["url"] == "https://example.com/article"
        assert result["tags"] == ["AI", "Tech"]

    def test_parse_entry_returns_none_for_empty_link(self):
        mock_entry = MagicMock()
        mock_entry.get.return_value = ""
        mock_feed = MagicMock()
        result = self.collector._parse_entry(mock_entry, mock_feed, "https://example.com/feed")
        assert result is None

    def test_parse_date_returns_utcnow_when_no_parsed_date(self):
        mock_entry = MagicMock()
        mock_entry.published_parsed = None
        result = self.collector._parse_date(mock_entry)
        assert result is not None

    def test_extract_tags_from_entry(self):
        mock_entry = MagicMock()
        mock_entry.get.return_value = [{"term": "AI"}, {"term": "LLM"}, {"term": ""}]
        result = self.collector._extract_tags(mock_entry)
        assert result == ["AI", "LLM"]

    def test_default_feeds_not_empty(self):
        assert len(self.collector.DEFAULT_FEEDS) > 0
        assert all(isinstance(url, str) for url in self.collector.DEFAULT_FEEDS)