"""Unit tests for the WeChat MessageHandler module.

Tests cover command routing, daily/weekly report generation,
and fallback to agent for unrecognized messages.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.wechat.handler import MessageHandler


@pytest.mark.unit
class TestMessageHandler:
    """Tests for MessageHandler class."""

    @pytest.fixture
    def handler(self) -> MessageHandler:
        """Create a MessageHandler instance with mocked agent."""
        with patch("src.wechat.handler.news_agent") as mock_agent:
            handler = MessageHandler()
            handler._agent = mock_agent
            return handler

    # --- handle() tests ---

    def test_handle_daily_report_command_returns_daily_summary(self, handler: MessageHandler) -> None:
        """handle() with '日报' command returns daily summary response."""
        # Arrange
        message = "日报"
        user_id = "test_user_123"

        # Act
        response = handler.handle(message, user_id)

        # Assert
        assert isinstance(response, str)
        assert len(response) > 0
        assert "今日摘要" in response

    def test_handle_weekly_report_command_returns_weekly_report(self, handler: MessageHandler) -> None:
        """handle() with '周报' command returns weekly report response."""
        # Arrange
        message = "周报"
        user_id = "test_user_456"

        # Act
        response = handler.handle(message, user_id)

        # Assert
        assert isinstance(response, str)
        assert len(response) > 0

    def test_handle_unknown_message_calls_fallback_to_agent(self, handler: MessageHandler) -> None:
        """handle() with unrecognized message delegates to _fallback_to_agent."""
        # Arrange
        unknown_message = "你好啊，今天天气怎么样？"
        user_id = "test_user_789"
        expected_response = "这是来自AI agent的回复"

        mock_agent_result = {
            "messages": [MagicMock(content=expected_response)]
        }
        handler._agent.invoke.return_value = mock_agent_result

        # Act
        response = handler.handle(unknown_message, user_id)

        # Assert
        assert response == expected_response
        handler._agent.invoke.assert_called_once()

    def test_handle_unknown_message_when_no_agent_available_returns_friendly_message(
        self,
    ) -> None:
        """handle() with no agent available returns friendly fallback message."""
        # Arrange
        handler = MessageHandler()
        handler._agent = None
        unknown_message = "随便说点什么"
        user_id = "test_user_no_agent"

        # Act
        response = handler.handle(unknown_message, user_id)

        # Assert
        assert isinstance(response, str)
        assert "我不知道怎么回答这个" in response

    # --- _check_command() tests ---

    def test_check_command_returns_method_name_for_known_commands(self, handler: MessageHandler) -> None:
        """_check_command() returns method name string for recognized commands."""
        # Arrange & Act & Assert
        assert handler._check_command("今日内容") == "_get_daily_summary"
        assert handler._check_command("今天有什么") == "_get_daily_summary"
        assert handler._check_command("日报") == "_get_daily_summary"
        assert handler._check_command("周报") == "_get_weekly_report"
        assert handler._check_command("每周总结") == "_get_weekly_report"

    def test_check_command_returns_none_for_unknown_message(self, handler: MessageHandler) -> None:
        """_check_command() returns None for unrecognized messages."""
        # Arrange
        unknown_messages = [
            "你好",
            "今天天气如何",
            "给我讲个笑话",
            "帮助",
        ]

        # Act & Assert
        for message in unknown_messages:
            assert handler._check_command(message) is None

    # --- _get_daily_summary() tests ---

    def test_get_daily_summary_returns_string(self, handler: MessageHandler) -> None:
        """_get_daily_summary() returns a non-empty string."""
        # Arrange
        user_id = "test_user_summary"

        # Act
        response = handler._get_daily_summary(user_id)

        # Assert
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_daily_summary_contains_expected_content(self, handler: MessageHandler) -> None:
        """_get_daily_summary() returns a string containing '今日摘要'."""
        # Arrange
        user_id = "test_user_content"

        # Act
        response = handler._get_daily_summary(user_id)

        # Assert
        assert "今日摘要" in response

    # --- _get_weekly_report() tests ---

    def test_get_weekly_report_returns_string(self, handler: MessageHandler) -> None:
        """_get_weekly_report() returns a non-empty string."""
        # Arrange
        user_id = "test_user_weekly"

        # Act
        response = handler._get_weekly_report(user_id)

        # Assert
        assert isinstance(response, str)
        assert len(response) > 0
