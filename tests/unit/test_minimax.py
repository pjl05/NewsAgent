"""单元测试 - MiniMax API 服务"""
import pytest
from unittest.mock import patch, AsyncMock

from src.services.minimax import MiniMaxService


class TestMiniMaxService:
    """MiniMaxService 测试"""

    @pytest.fixture
    def service(self, mock_settings):
        """创建服务实例"""
        with patch("src.services.minimax.get_settings", return_value=mock_settings):
            return MiniMaxService()

    @pytest.mark.asyncio
    async def test_chat(self, service):
        """测试聊天功能"""
        mock_response_data = {
            "choices": [
                {"message": {"content": "Hello, this is a test response"}}
            ]
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.chat([{"role": "user", "content": "hello"}])
            assert "test response" in result

    @pytest.mark.asyncio
    async def test_get_embedding(self, service):
        """测试获取 embedding"""
        mock_response_data = {
            "data": [
                {"embedding": [0.1] * 1536}
            ]
        }

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.get_embedding("test text")
            assert len(result) == 1536
            assert result[0] == 0.1

    @pytest.mark.asyncio
    async def test_text_to_speech(self, service):
        """测试文字转语音"""
        mock_audio = b"fake audio content"

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = mock_audio

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service.text_to_speech("test text")
            assert result == mock_audio
