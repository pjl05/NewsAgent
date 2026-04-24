"""Unit tests for the Summarizer class."""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.asyncio
class TestSummarizer:
    """Tests for Summarizer.summarize() and summarize_batch()."""

    async def test_summarize_returns_string(self):
        """summarize returns a string."""
        from src.generator.summarizer import Summarizer

        with patch("src.generator.summarizer.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value="这是一个摘要")
            mock_minimax.return_value = mock_service

            summarizer = Summarizer()
            result = await summarizer.summarize("测试内容", max_words=100)

            assert isinstance(result, str)

    async def test_summarize_llm_error_returns_empty_string(self):
        """LLM exception returns empty string gracefully."""
        from src.generator.summarizer import Summarizer

        with patch("src.generator.summarizer.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(side_effect=Exception("API error"))
            mock_minimax.return_value = mock_service

            summarizer = Summarizer()
            result = await summarizer.summarize("测试内容")

            assert result == ""

    async def test_summarize_batch_empty_input(self):
        """Batch summarize with empty list returns empty list without calling LLM."""
        from src.generator.summarizer import Summarizer

        with patch("src.generator.summarizer.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_minimax.return_value = mock_service

            summarizer = Summarizer()
            results = await summarizer.summarize_batch([])

            assert results == []

    async def test_summarize_batch_multiple_contents(self):
        """Batch summarize calls LLM for each content in parallel."""
        from src.generator.summarizer import Summarizer

        with patch("src.generator.summarizer.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value="测试摘要")
            mock_minimax.return_value = mock_service

            summarizer = Summarizer()
            contents = ["内容一", "内容二"]
            results = await summarizer.summarize_batch(contents, max_words=50)

            assert len(results) == 2
            assert mock_service.chat.call_count == 2

    async def test_summarize_batch_respects_max_words(self):
        """Each prompt in batch uses the max_words parameter."""
        from src.generator.summarizer import Summarizer

        with patch("src.generator.summarizer.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.chat = AsyncMock(return_value="摘要")
            mock_minimax.return_value = mock_service

            summarizer = Summarizer()
            await summarizer.summarize_batch(["内容1", "内容2"], max_words=25)

            calls = mock_service.chat.call_args_list
            assert len(calls) == 2
            # Each call receives messages=[{"role": "user", "content": <prompt>}]
            for call in calls:
                args, kwargs = call
                messages = args[0] if args else kwargs.get("messages")
                content = messages[0]["content"]
                assert "25字以内" in content
