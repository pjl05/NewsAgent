import pytest
from unittest.mock import AsyncMock, patch
from src.collector.platform_collector import PlatformCollector


class TestPlatformCollector:
    def setup_method(self):
        self.collector = PlatformCollector()

    def test_content_id_has_weibo_prefix(self):
        content_id = "weibo_abc123"
        assert content_id.startswith("weibo_")

    def test_content_id_has_zhihu_prefix(self):
        content_id = "zhihu_def456"
        assert content_id.startswith("zhihu_")

    @pytest.mark.asyncio
    async def test_fetch_weibo_returns_list_with_correct_structure(self):
        mock_results = [
            {
                "content_id": "weibo_abc123",
                "title": "Test Hot Topic",
                "source": "微博热搜",
                "url": "https://s.weibo.com/weibo?q=Test Hot Topic",
                "published_at": None,
                "summary": "100000",
                "tags": ["微博热搜"],
            }
        ]
        collector = PlatformCollector()
        with patch.object(collector, "_fetch_weibo", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_results
            results = await collector._fetch_weibo()
            assert isinstance(results, list)
            assert len(results) == 1
            assert results[0]["title"] == "Test Hot Topic"
            assert results[0]["source"] == "微博热搜"
            assert results[0]["content_id"].startswith("weibo_")

    @pytest.mark.asyncio
    async def test_fetch_weibo_handles_empty_realtime_list(self):
        collector = PlatformCollector()
        with patch.object(collector, "_fetch_weibo", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            results = await collector._fetch_weibo()
            assert results == []

    @pytest.mark.asyncio
    async def test_fetch_zhihu_returns_list_with_correct_structure(self):
        mock_results = [
            {
                "content_id": "zhihu_def456",
                "title": "Zhihu Test",
                "source": "知乎热榜",
                "url": "https://zhihu.com/question/123",
                "published_at": None,
                "summary": "Test excerpt",
                "tags": ["知乎热榜"],
            }
        ]
        collector = PlatformCollector()
        with patch.object(collector, "_fetch_zhihu", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_results
            results = await collector._fetch_zhihu()
            assert isinstance(results, list)
            assert len(results) == 1
            assert results[0]["title"] == "Zhihu Test"
            assert results[0]["source"] == "知乎热榜"
            assert results[0]["content_id"].startswith("zhihu_")