"""Summarizer — generates concise summaries from content text using MiniMax LLM."""

import asyncio
import logging
from typing import List

from src.services.minimax import get_minimax

logger = logging.getLogger(__name__)


class Summarizer:
    """Generates concise summaries from content using MiniMax LLM."""

    def __init__(self, model: str = "abab6.5s-chat") -> None:
        self._model = model
        self._minimax = get_minimax()

    async def _call_llm(self, prompt: str) -> str:
        """Internal: call MiniMax chat and return content string, or "" on error."""
        try:
            messages = [{"role": "user", "content": prompt}]
            return await self._minimax.chat(messages, temperature=0.3)
        except Exception as e:
            logger.error("Summarizer LLM call failed: %s", e)
            return ""

    async def summarize(self, content: str, max_words: int = 100) -> str:
        """Generate a concise summary of the given content text.

        Args:
            content: The source text to summarize.
            max_words: Maximum word count for the summary (default 100).

        Returns:
            The summary string, or empty string if the API call fails.
        """
        prompt = (
            f"请用{max_words}字以内总结以下内容，要求简洁、有信息量：\n{content}\n摘要："
        )
        return await self._call_llm(prompt)

    async def summarize_batch(
        self, contents: List[str], max_words: int = 100
    ) -> List[str]:
        """Generate summaries for multiple content texts in parallel.

        Args:
            contents: List of source texts to summarize.
            max_words: Maximum word count per summary (default 100).

        Returns:
            List of summary strings (empty string for any that fail).
        """
        if not contents:
            return []

        prompts = [
            f"请用{max_words}字以内总结以下内容，要求简洁、有信息量：\n{c}\n摘要："
            for c in contents
        ]

        results: List[str] = await asyncio.gather(
            *(self._call_llm(p) for p in prompts), return_exceptions=False
        )
        return list(results)