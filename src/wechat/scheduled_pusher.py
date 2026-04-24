from __future__ import annotations

import logging
from typing import List, Dict, Any

from src.wechat.wechat_client import WeChatClient
from src.wechat.handler import MessageHandler

logger = logging.getLogger(__name__)


class ScheduledPusher:
    """定时推送服务，向微信用户发送日报/周报消息"""

    def __init__(self) -> None:
        self.wechat = WeChatClient()
        self.handler = MessageHandler()

    def push_daily(self, user_ids: List[str]) -> Dict[str, int]:
        """
        向指定用户列表发送日报

        Args:
            user_ids: 用户的 OpenID 列表

        Returns:
            包含 success 和 failure 数量的摘要字典
        """
        success_count = 0
        failure_count = 0

        for user_id in user_ids:
            try:
                summary = self.handler._get_daily_summary(user_id)
                result = self.wechat.send_message(user_id, summary)
                if result.get("errcode") == 0:
                    success_count += 1
                    logger.debug("[push_daily] 成功发送给用户 %s", user_id)
                else:
                    failure_count += 1
                    logger.warning(
                        "[push_daily] 发送失败，用户 %s，错误码: %s",
                        user_id,
                        result.get("errmsg"),
                    )
            except Exception as e:
                failure_count += 1
                logger.error("[push_daily] 推送异常，用户 %s: %s", user_id, e)

        logger.info(
            "[push_daily] 完成，成功: %d，失败: %d",
            success_count,
            failure_count,
        )
        return {"success": success_count, "failure": failure_count}

    def push_weekly(self, user_ids: List[str]) -> Dict[str, int]:
        """
        向指定用户列表发送周报

        Args:
            user_ids: 用户的 OpenID 列表

        Returns:
            包含 success 和 failure 数量的摘要字典
        """
        success_count = 0
        failure_count = 0

        for user_id in user_ids:
            try:
                report = self.handler._get_weekly_report(user_id)
                result = self.wechat.send_message(user_id, report)
                if result.get("errcode") == 0:
                    success_count += 1
                    logger.debug("[push_weekly] 成功发送给用户 %s", user_id)
                else:
                    failure_count += 1
                    logger.warning(
                        "[push_weekly] 发送失败，用户 %s，错误码: %s",
                        user_id,
                        result.get("errmsg"),
                    )
            except Exception as e:
                failure_count += 1
                logger.error("[push_weekly] 推送异常，用户 %s: %s", user_id, e)

        logger.info(
            "[push_weekly] 完成，成功: %d，失败: %d",
            success_count,
            failure_count,
        )
        return {"success": success_count, "failure": failure_count}