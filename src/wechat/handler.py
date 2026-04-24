"""WeChat message handler module.

Implements the MessageHandler class per Phase 5 spec 5.3.2.
Handles text messages from WeChat users and routes them to appropriate handlers.
"""

import logging
from typing import Optional

from src.agent.graph import news_agent

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles WeChat text messages and routes commands to appropriate handlers.

    Supports the following commands:
        - 今日内容 / 今天有什么 / 日报 -> _get_daily_summary
        - 周报 / 每周总结 -> _get_weekly_report

    All other messages are passed to the news agent for processing.
    """

    COMMANDS: dict[str, str] = {
        "今日内容": "_get_daily_summary",
        "今天有什么": "_get_daily_summary",
        "日报": "_get_daily_summary",
        "周报": "_get_weekly_report",
        "每周总结": "_get_weekly_report",
    }

    def __init__(self) -> None:
        """Initialize the MessageHandler with the news agent.

        Falls back to None if the agent is not available, in which case
        unknown messages will return a friendly error message.
        """
        self._agent: Optional[object] = None
        try:
            # agent is the compiled LangGraph from src.agent.graph
            self._agent = news_agent
            logger.info("MessageHandler initialized with news_agent")
        except Exception as e:
            logger.warning("Failed to load news_agent, falling back to friendly messages: %s", e)

    def handle(self, message: str, user_id: str) -> str:
        """Handle an incoming WeChat text message.

        Args:
            message: The text content of the incoming WeChat message.
            user_id: The WeChat openid/user_id of the sender.

        Returns:
            A text response to send back to the user.
        """
        logger.debug("Handling message from user %s: %s", user_id, message)

        command = self._check_command(message)
        if command is not None:
            logger.debug("Command matched: %s -> %s", message, command)
            return getattr(self, command)(user_id)

        return self._fallback_to_agent(message, user_id)

    def _check_command(self, message: str) -> Optional[str]:
        """Check if the message matches a known command.

        Args:
            message: The raw text message.

        Returns:
            The name of the handler method to call, or None if no match.
        """
        return self.COMMANDS.get(message)

    def _get_daily_summary(self, user_id: str) -> str:
        """Generate and return a daily summary for the given user.

        Args:
            user_id: The user identifier.

        Returns:
            A formatted daily summary string.
        """
        logger.info("Generating daily summary for user %s", user_id)
        # TODO: Integrate with recommendation engine to fetch personalized daily content
        return (
            "今日摘要：\n"
            "1. [AI突破] OpenAI发布新模型...\n"
            "2. [科技股] 英伟达财报超预期...\n"
            "\n"
            "想看更多内容？试试发送「日报」或「周报」~"
        )

    def _get_weekly_report(self, user_id: str) -> str:
        """Generate and return a weekly report for the given user.

        Args:
            user_id: The user identifier.

        Returns:
            A formatted weekly report string.
        """
        logger.info("Generating weekly report for user %s", user_id)
        # TODO: Integrate with recommendation engine to fetch personalized weekly content
        return "周报功能开发中，即将上线。"

    def _fallback_to_agent(self, message: str, user_id: str) -> str:
        """Pass an unrecognized message to the news agent.

        Args:
            message: The unrecognized text message.
            user_id: The user identifier.

        Returns:
            The agent's response, or a friendly message on failure.
        """
        if self._agent is None:
            logger.debug("No agent available, returning friendly unknown message")
            return "我不知道怎么回答这个。试试发送「今日内容」或「周报」看看有什么~"

        try:
            # LangGraph agent expects {"messages": [HumanMessage(content=...)]}
            from langchain_core.messages import HumanMessage

            result = self._agent.invoke({"messages": [HumanMessage(content=message)]})
            # The news_agent returns {"messages": [AIMessage(...)]}
            response = result.get("messages", [])[-1].content if result.get("messages") else ""
            if not response:
                return "我不知道怎么回答这个。试试发送「今日内容」或「周报」看看有什么~"
            return response
        except Exception as e:
            logger.exception("Agent invoke failed for message from user %s: %s", user_id, e)
            return "我不知道怎么回答这个。试试发送「今日内容」或「周报」看看有什么~"
