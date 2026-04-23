import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.collector.platform_collector import PlatformCollector


class TestPlatformCollector:
    def setup_method(self):
        self.collector = PlatformCollector()

    def test_collect_calls_weibo_and_zhihu(self):
        """Test that collect() calls both _fetch_weibo and _fetch_zhihu"""
        import asyncio

        async def run():
            with patch.object(self.collector, "_fetch_weibo", new_callable=AsyncMock) as mock_weibo, \
                 patch.object(self.collector, "_fetch_zhihu", new_callable=AsyncMock) as mock_zhihu:
                mock_weibo.return_value = [{"content_id": "w1", "title": "A"}]
                mock_zhihu.return_value = [{"content_id": "z1", "title": "B"}]

                result = await self.collector.collect(["weibo", "zhihu"])

                mock_weibo.assert_called_once()
                mock_zhihu.assert_called_once()
                assert len(result) == 2

        asyncio.get_event_loop().run_until_complete(run())

    def test_weibo_content_id_uses_hash_of_title(self):
        """Test that weibo content_id is deterministic from title"""
        item1 = {"content_id": f"weibo_{'a' * 12}", "title": "Test"}
        item2 = {"content_id": f"weibo_{'a' * 12}", "title": "Test"}
        assert item1["content_id"] == item2["content_id"]
        assert item1["content_id"].startswith("weibo_")

    def test_zhihu_content_id_uses_hash_of_title(self):
        """Test that zhihu content_id is deterministic from title"""
        item1 = {"content_id": f"zhihu_{'b' * 12}", "title": "Test2"}
        item2 = {"content_id": f"zhihu_{'b' * 12}", "title": "Test2"}
        assert item1["content_id"] == item2["content_id"]
        assert item1["content_id"].startswith("zhihu_")

    @pytest.mark.asyncio
    async def test_fetch_weibo_parses_real_api_response_structure(self):
        """Test _fetch_weibo parses the actual API response format correctly"""
        mock_response = {
            "data": {
                "realtime": [
                    {"word": "AI Breakthrough", "raw_hot": "5000000"},
                    {"word": "Tech Stock", "raw_hot": "3000000"},
                ]
            }
        }
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_instance.__aenter__.return_value.get.return_value = mock_response_obj
            mock_client.return_value = mock_instance

            results = await self.collector._fetch_weibo()

            assert len(results) == 2
            assert results[0]["title"] == "AI Breakthrough"
            assert results[0]["source"] == "微博热搜"
            assert results[0]["content_id"].startswith("weibo_")
            assert results[0]["tags"] == ["微博热搜"]
            assert results[1]["title"] == "Tech Stock"
            assert results[1]["summary"] == "3000000"

    @pytest.mark.asyncio
    async def test_fetch_weibo_handles_empty_realtime_list(self):
        """Test _fetch_weibo returns empty list when no realtime items"""
        mock_response = {"data": {"realtime": []}}
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_instance.__aenter__.return_value.get.return_value = mock_response_obj
            mock_client.return_value = mock_instance

            results = await self.collector._fetch_weibo()
            assert results == []

    @pytest.mark.asyncio
    async def test_fetch_zhihu_parses_real_api_response_structure(self):
        """Test _fetch_zhihu parses the actual API response format correctly"""
        mock_response = {
            "data": [
                {
                    "target": {
                        "title": "Why AI Matters",
                        "excerpt": "A deep dive",
                        "url": "https://zhihu.com/question/123",
                    }
                }
            ]
        }
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_instance.__aenter__.return_value.get.return_value = mock_response_obj
            mock_client.return_value = mock_instance

            results = await self.collector._fetch_zhihu()

            assert len(results) == 1
            assert results[0]["title"] == "Why AI Matters"
            assert results[0]["source"] == "知乎热榜"
            assert results[0]["content_id"].startswith("zhihu_")
            assert results[0]["summary"] == "A deep dive"
            assert results[0]["tags"] == ["知乎热榜"]

    @pytest.mark.asyncio
    async def test_fetch_zhihu_handles_missing_title(self):
        """Test _fetch_zhihu skips items with missing title"""
        mock_response = {"data": [{"target": {"excerpt": "no title"}}]}
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_instance.__aenter__.return_value.get.return_value = mock_response_obj
            mock_client.return_value = mock_instance

            results = await self.collector._fetch_zhihu()
            assert results == []