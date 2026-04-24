"""单元测试 - WeChat 客户端"""
import pytest
import time
from unittest.mock import patch, MagicMock

from src.wechat.wechat_client import WeChatClient, WeChatAPIError


@pytest.fixture
def mock_settings():
    """模拟 WeChat 设置"""
    settings = MagicMock()
    settings.wechat_app_id = "test-wechat-app-id"
    settings.wechat_app_secret = "test-wechat-app-secret"
    return settings


@pytest.fixture
def client(mock_settings):
    """创建 WeChatClient 实例"""
    with patch("src.wechat.wechat_client.get_settings", return_value=mock_settings):
        return WeChatClient()


class TestWeChatClientGetAccessToken:
    """WeChatClient.get_access_token() 测试"""

    @pytest.mark.unit
    def test_get_access_token_success(self, client):
        """获取 access token 成功"""
        # Arrange
        mock_response_data = {
            "access_token": "test_token_12345",
            "expires_in": 7200,
            "errcode": 0,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act
            token = client.get_access_token()

        # Assert
        assert token == "test_token_12345"
        assert client._access_token == "test_token_12345"
        mock_client.get.assert_called_once()

    @pytest.mark.unit
    def test_get_access_token_error_from_api(self, client):
        """API 返回错误码时抛出 WeChatAPIError"""
        # Arrange
        mock_response_data = {
            "errcode": 40013,
            "errmsg": "invalid appid",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act & Assert
            with pytest.raises(WeChatAPIError) as exc_info:
                client.get_access_token()
            assert exc_info.value.errcode == 40013
            assert "invalid appid" in exc_info.value.errmsg

    @pytest.mark.unit
    def test_get_access_token_http_error(self, client):
        """HTTP 状态码错误时抛出 WeChatAPIError"""
        # Arrange
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(),
        ))

        with patch("httpx.Client", return_value=mock_client):
            # Act & Assert
            with pytest.raises(WeChatAPIError) as exc_info:
                client.get_access_token()
            assert "HTTP error" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_access_token_missing_field(self, client):
        """响应缺少 access_token 字段时抛出 WeChatAPIError"""
        # Arrange
        mock_response_data = {
            "expires_in": 7200,
            "errcode": 0,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act & Assert
            with pytest.raises(WeChatAPIError) as exc_info:
                client.get_access_token()
            assert "missing" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_access_token_is_cached(self, client):
        """token 在有效期内不重复请求 API"""
        # Arrange
        mock_response_data = {
            "access_token": "cached_token",
            "expires_in": 7200,
            "errcode": 0,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act - 首次获取
            token1 = client.get_access_token()
            # Act - 再次获取（应使用缓存）
            token2 = client.get_access_token()

        # Assert
        assert token1 == token2 == "cached_token"
        # 只应调用一次 API
        assert mock_client.get.call_count == 1

    @pytest.mark.unit
    def test_access_token_refreshed_early(self, client):
        """token 过期后再次调用会获取新 token"""
        # Arrange - 设置一个已过期的 token (expired 60s early means _token_expires_at is in the past)
        client._access_token = "old_token"
        client._token_expires_at = time.time() - 1  # 已过期，触发刷新

        mock_response_data = {
            "access_token": "new_token",
            "expires_in": 7200,
            "errcode": 0,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act
            token = client.get_access_token()

        # Assert
        assert token == "new_token"
        assert mock_client.get.call_count == 1

    @pytest.mark.unit
    def test_correct_url_and_params_sent(self, client):
        """验证获取 token 时发送了正确的 URL 和参数"""
        # Arrange
        mock_response_data = {
            "access_token": "test_token",
            "expires_in": 7200,
            "errcode": 0,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            client.get_access_token()

        # Assert - 验证 URL
        call_args = mock_client.get.call_args
        url = call_args[0][0]
        params = call_args[1]["params"]

        assert "api.weixin.qq.com/cgi-bin/token" in url
        assert params["grant_type"] == "client_credential"
        assert params["appid"] == "test-wechat-app-id"
        assert params["secret"] == "test-wechat-app-secret"


class TestWeChatClientSendMessage:
    """WeChatClient.send_message() 测试"""

    @pytest.mark.unit
    def test_send_message_success(self, client):
        """发送消息成功"""
        # Arrange
        client._access_token = "valid_token"
        client._token_expires_at = time.time() + 3600

        mock_response_data = {
            "errcode": 0,
            "errmsg": "ok",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act
            result = client.send_message("openid_123", "Hello WeChat")

        # Assert
        assert result["errcode"] == 0
        mock_client.post.assert_called_once()

    @pytest.mark.unit
    def test_send_message_error_from_api(self, client):
        """API 返回错误码时抛出 WeChatAPIError"""
        # Arrange
        client._access_token = "valid_token"
        client._token_expires_at = time.time() + 3600

        mock_response_data = {
            "errcode": 40003,
            "errmsg": "invalid openid",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act & Assert
            with pytest.raises(WeChatAPIError) as exc_info:
                client.send_message("invalid_openid", "Hello")
            assert exc_info.value.errcode == 40003
            assert "invalid openid" in exc_info.value.errmsg

    @pytest.mark.unit
    def test_send_message_http_error(self, client):
        """HTTP 错误时抛出 WeChatAPIError"""
        # Arrange
        client._access_token = "valid_token"
        client._token_expires_at = time.time() + 3600

        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post = MagicMock(side_effect=httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=MagicMock(),
        ))

        with patch("httpx.Client", return_value=mock_client):
            # Act & Assert
            with pytest.raises(WeChatAPIError) as exc_info:
                client.send_message("openid_123", "Hello")
            assert "HTTP error" in str(exc_info.value)

    @pytest.mark.unit
    def test_send_message_correct_payload(self, client):
        """验证发送消息时使用了正确的 URL 和 payload"""
        # Arrange
        client._access_token = "test_token"
        client._token_expires_at = time.time() + 3600

        mock_response_data = {"errcode": 0, "errmsg": "ok"}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.post = MagicMock(return_value=mock_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act
            client.send_message("user_openid_abc", "Test message content")

        # Assert
        call_args = mock_client.post.call_args
        url = call_args[0][0]
        payload = call_args[1]["json"]

        assert "access_token=test_token" in url
        assert payload["touser"] == "user_openid_abc"
        assert payload["msgtype"] == "text"
        assert payload["text"]["content"] == "Test message content"

    @pytest.mark.unit
    def test_send_message_fetches_token_if_not_cached(self, client):
        """未缓存 token 时先获取 token 再发送消息"""
        # Arrange - 没有缓存的 token
        client._access_token = None
        client._token_expires_at = 0.0

        # Token 获取响应
        token_response_data = {
            "access_token": "fetched_token",
            "expires_in": 7200,
            "errcode": 0,
        }
        token_response = MagicMock()
        token_response.json.return_value = token_response_data
        token_response.raise_for_status = MagicMock()

        # 消息发送响应
        msg_response_data = {"errcode": 0, "errmsg": "ok"}
        msg_response = MagicMock()
        msg_response.json.return_value = msg_response_data
        msg_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=token_response)
        mock_client.post = MagicMock(return_value=msg_response)

        with patch("httpx.Client", return_value=mock_client):
            # Act
            result = client.send_message("openid_123", "Hello")

        # Assert
        assert result["errcode"] == 0
        assert mock_client.get.call_count == 1
        assert mock_client.post.call_count == 1
        # 验证 token 被用于消息发送
        post_url = mock_client.post.call_args[0][0]
        assert "access_token=fetched_token" in post_url


class TestWeChatAPIError:
    """WeChatAPIError 异常测试"""

    @pytest.mark.unit
    def test_wechat_api_error_attributes(self):
        """验证 WeChatAPIError 包含 errcode 和 errmsg 属性"""
        # Arrange & Act
        error = WeChatAPIError("test error", errcode=40001, errmsg="test errmsg")

        # Assert
        assert error.errcode == 40001
        assert error.errmsg == "test errmsg"
        assert str(error) == "test error"

    @pytest.mark.unit
    def test_wechat_api_error_without_code(self):
        """验证 WeChatAPIError 可以没有错误码"""
        # Arrange & Act
        error = WeChatAPIError("generic error")

        # Assert
        assert error.errcode is None
        assert error.errmsg is None