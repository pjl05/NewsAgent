import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.collector.search_collector import SearchCollector


class TestSearchCollector:
    def setup_method(self):
        self.collector = SearchCollector()

    @pytest.mark.asyncio
    async def test_collect_uses_bing_when_key_set(self):
        """Test that collect() uses Bing when bing_api_key is set"""
        with patch("src.collector.search_collector.settings") as mock_settings:
            mock_settings.bing_api_key = "test_key_123"
            with patch.object(self.collector, "_search_bing", new_callable=AsyncMock) as mock_bing:
                mock_bing.return_value = [{"content_id": "b_123", "title": "Result"}]
                result = await self.collector.collect(["AI news"])
                mock_bing.assert_called_once_with("AI news")
                assert len(result) == 1

    @pytest.mark.asyncio
    async def test_collect_falls_back_to_duckduckgo_when_no_key(self):
        """Test that collect() falls back to DuckDuckGo when no bing_api_key"""
        with patch("src.collector.search_collector.settings") as mock_settings:
            mock_settings.bing_api_key = ""
            with patch.object(self.collector, "_search_duckduckgo", new_callable=AsyncMock) as mock_ddg:
                mock_ddg.return_value = [{"content_id": "d_123", "title": "Result"}]
                result = await self.collector.collect(["AI news"])
                mock_ddg.assert_called_once_with("AI news")
                assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_bing_returns_list_with_correct_structure(self):
        """Test _search_bing parses Bing API response correctly"""
        mock_response = {
            "webPages": {
                "value": [
                    {
                        "name": "AI Breakthrough",
                        "displayUrl": "https://news.example.com/ai",
                        "url": "https://news.example.com/ai",
                        "snippet": "Major AI discovery announced",
                    }
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

            results = await self.collector._search_bing("AI news")

            assert len(results) == 1
            assert results[0]["title"] == "AI Breakthrough"
            assert results[0]["source"] == "https://news.example.com/ai"
            assert results[0]["content_id"].startswith("bing_")
            assert results[0]["tags"] == ["AI news"]

    @pytest.mark.asyncio
    async def test_search_duckduckgo_returns_list_with_correct_structure(self):
        """Test _search_duckduckgo parses HTML correctly"""
        html = """
        <html><body>
            <div class="result">
                <div class="result__title"><a href="https://example.com/article">Example Article</a></div>
                <div class="result__snippet">This is a snippet.</div>
            </div>
        </body></html>
        """
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.text = html
            mock_response_obj.raise_for_status = MagicMock()
            mock_instance.__aenter__.return_value.get.return_value = mock_response_obj
            mock_client.return_value = mock_instance

            results = await self.collector._search_duckduckgo("test query")

            assert len(results) == 1
            assert results[0]["title"] == "Example Article"
            assert results[0]["source"] == "DuckDuckGo"
            assert results[0]["content_id"].startswith("ddg_")
            assert results[0]["summary"] == "This is a snippet."