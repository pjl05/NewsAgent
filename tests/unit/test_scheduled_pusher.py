"""Unit tests for the ScheduledPusher class."""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.unit
class TestScheduledPusher:
    """Tests for ScheduledPusher.push_daily() and push_weekly()."""

    def _make_mock_wechat(self, errcode: int = 0) -> MagicMock:
        """Build a mock WeChatClient whose send_message returns a fixed errcode-based response."""
        mock_instance = MagicMock()
        # side_effect as a callable ignores the call args and returns the fixed dict.
        mock_instance.send_message.side_effect = lambda uid, msg: {"errcode": errcode, "errmsg": "ok"}
        return mock_instance

    def _make_mock_handler(self) -> MagicMock:
        """Build a mock MessageHandler with no-op summary/report generators."""
        return MagicMock()

    def _build_pusher(self, mock_wechat: MagicMock, mock_handler: MagicMock):
        """Construct a ScheduledPusher and inject the given mock instances as its dependencies."""
        with patch("src.wechat.scheduled_pusher.WeChatClient", return_value=mock_wechat):
            with patch("src.wechat.scheduled_pusher.MessageHandler", return_value=mock_handler):
                from src.wechat.scheduled_pusher import ScheduledPusher
                pusher = ScheduledPusher()
                # __init__ ran and created real instances — replace them.
                pusher.wechat = mock_wechat
                pusher.handler = mock_handler
                return pusher

    # -------------------------------------------------------------------------
    # push_daily tests
    # -------------------------------------------------------------------------

    def test_push_daily_returns_success_failure_counts_for_empty_user_list(self):
        """push_daily with no users returns zero counts."""
        wechat_mock = self._make_mock_wechat()
        handler_mock = self._make_mock_handler()
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_daily([])

        assert result == {"success": 0, "failure": 0}
        handler_mock._get_daily_summary.assert_not_called()
        wechat_mock.send_message.assert_not_called()

    def test_push_daily_all_users_succeed(self):
        """push_daily counts every user as success when all send_message calls return errcode 0."""
        wechat_mock = self._make_mock_wechat(errcode=0)
        handler_mock = self._make_mock_handler()
        handler_mock._get_daily_summary.return_value = "今日摘要：测试内容"
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_daily(["user1", "user2", "user3"])

        assert result == {"success": 3, "failure": 0}
        assert handler_mock._get_daily_summary.call_count == 3
        assert wechat_mock.send_message.call_count == 3
        for user_id in ["user1", "user2", "user3"]:
            wechat_mock.send_message.assert_any_call(user_id, "今日摘要：测试内容")

    def test_push_daily_partial_failure_due_to_nonzero_errcode(self):
        """push_daily counts a user as failure when send_message returns a non-zero errcode."""
        wechat_mock = MagicMock()
        handler_mock = self._make_mock_handler()
        handler_mock._get_daily_summary.return_value = "今日摘要"
        # side_effect list returns a different response for each call.
        wechat_mock.send_message.side_effect = [
            {"errcode": 0, "errmsg": "ok"},
            {"errcode": 40001, "errmsg": "invalid credential"},
            {"errcode": 0, "errmsg": "ok"},
        ]
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_daily(["user1", "user2", "user3"])

        assert result == {"success": 2, "failure": 1}

    def test_push_daily_continues_after_exception(self):
        """push_daily processes remaining users when one user raises an exception."""
        wechat_mock = MagicMock()
        handler_mock = self._make_mock_handler()
        handler_mock._get_daily_summary.side_effect = [
            Exception("DB connection failed"),
            "今日摘要 - user2",
            "今日摘要 - user3",
        ]
        wechat_mock.send_message.side_effect = [
            {"errcode": 0},
            Exception("Network timeout"),
            {"errcode": 0},
        ]
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_daily(["user1", "user2", "user3"])

        assert result == {"success": 1, "failure": 2}

    # -------------------------------------------------------------------------
    # push_weekly tests
    # -------------------------------------------------------------------------

    def test_push_weekly_returns_success_failure_counts_for_empty_user_list(self):
        """push_weekly with no users returns zero counts."""
        wechat_mock = self._make_mock_wechat()
        handler_mock = self._make_mock_handler()
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_weekly([])

        assert result == {"success": 0, "failure": 0}
        handler_mock._get_weekly_report.assert_not_called()
        wechat_mock.send_message.assert_not_called()

    def test_push_weekly_all_users_succeed(self):
        """push_weekly counts every user as success when all send_message calls return errcode 0."""
        wechat_mock = self._make_mock_wechat(errcode=0)
        handler_mock = self._make_mock_handler()
        handler_mock._get_weekly_report.return_value = "周报功能开发中，即将上线。"
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_weekly(["user_a", "user_b"])

        assert result == {"success": 2, "failure": 0}
        assert handler_mock._get_weekly_report.call_count == 2
        assert wechat_mock.send_message.call_count == 2
        for user_id in ["user_a", "user_b"]:
            wechat_mock.send_message.assert_any_call(user_id, "周报功能开发中，即将上线。")

    def test_push_weekly_partial_failure_due_to_nonzero_errcode(self):
        """push_weekly counts a user as failure when send_message returns a non-zero errcode."""
        wechat_mock = MagicMock()
        handler_mock = self._make_mock_handler()
        handler_mock._get_weekly_report.return_value = "周报内容"
        wechat_mock.send_message.side_effect = [
            {"errcode": 0, "errmsg": "ok"},
            {"errcode": 40003, "errmsg": "invalid openid"},
        ]
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_weekly(["user_x", "user_y"])

        assert result == {"success": 1, "failure": 1}

    def test_push_weekly_continues_after_exception(self):
        """push_weekly processes remaining users when one user raises an exception."""
        wechat_mock = MagicMock()
        handler_mock = self._make_mock_handler()
        handler_mock._get_weekly_report.side_effect = [
            "周报 - user1",
            Exception("handler error for user2"),
            "周报 - user3",
        ]
        wechat_mock.send_message.side_effect = [
            Exception("send error for user1"),
            {"errcode": 0},
            {"errcode": 0},
        ]
        pusher = self._build_pusher(wechat_mock, handler_mock)

        result = pusher.push_weekly(["user1", "user2", "user3"])

        assert result == {"success": 1, "failure": 2}

    def test_push_daily_and_push_weekly_call_correct_handler_methods(self):
        """push_daily calls _get_daily_summary; push_weekly calls _get_weekly_report."""
        wechat_mock = self._make_mock_wechat(errcode=0)
        handler_mock = self._make_mock_handler()
        handler_mock._get_daily_summary.return_value = "daily"
        handler_mock._get_weekly_report.return_value = "weekly"
        pusher = self._build_pusher(wechat_mock, handler_mock)

        pusher.push_daily(["u1"])
        pusher.push_weekly(["u2"])

        handler_mock._get_daily_summary.assert_called_once_with("u1")
        handler_mock._get_weekly_report.assert_called_once_with("u2")
        wechat_mock.send_message.assert_any_call("u1", "daily")
        wechat_mock.send_message.assert_any_call("u2", "weekly")
