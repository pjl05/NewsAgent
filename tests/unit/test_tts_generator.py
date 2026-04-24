"""Unit tests for the TTSGenerator class."""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestTTSGenerator:
    """Tests for TTSGenerator.generate()."""

    def test_generate_returns_filepath_on_success(self, tmp_path):
        """Successful TTS returns a file path string."""
        from src.generator.tts_generator import TTSGenerator

        mock_audio = b"fake mp3 audio bytes"

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(return_value=mock_audio)
            mock_minimax.return_value = mock_service

            tts_gen = TTSGenerator(output_dir=str(tmp_path))
            result = tts_gen.generate("测试文本")

            assert isinstance(result, str)
            assert result.endswith(".mp3")
            # Verify the returned path contains the output_dir
            assert str(tmp_path) in result

    def test_generate_returns_empty_string_on_error(self, tmp_path):
        """TTS failure returns empty string without raising."""
        from src.generator.tts_generator import TTSGenerator

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(side_effect=Exception("API error"))
            mock_minimax.return_value = mock_service

            tts_gen = TTSGenerator(output_dir=str(tmp_path))
            result = tts_gen.generate("测试文本")

            assert result == ""

    def test_generate_uses_provided_voice_id(self, tmp_path):
        """generate() passes voice_id to the TTS API."""
        from src.generator.tts_generator import TTSGenerator

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(return_value=b"audio")
            mock_minimax.return_value = mock_service

            tts_gen = TTSGenerator(output_dir=str(tmp_path))
            tts_gen.generate("测试文本", voice_id="custom_voice")

            mock_service.text_to_speech.assert_called_once_with("测试文本", "custom_voice")

    def test_generate_uses_default_voice_id(self, tmp_path):
        """generate() uses default voice when not specified."""
        from src.generator.tts_generator import TTSGenerator

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(return_value=b"audio")
            mock_minimax.return_value = mock_service

            tts_gen = TTSGenerator(output_dir=str(tmp_path))
            tts_gen.generate("测试文本")

            mock_service.text_to_speech.assert_called_once_with(
                "测试文本", "English_expressive_narrator"
            )

    def test_generate_idempotent_same_text(self, tmp_path):
        """Same text always produces same filename (MD5 hash)."""
        from src.generator.tts_generator import TTSGenerator

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(return_value=b"audio")
            mock_minimax.return_value = mock_service

            tts_gen = TTSGenerator(output_dir=str(tmp_path))
            result1 = tts_gen.generate("相同文本")
            result2 = tts_gen.generate("相同文本")

            assert result1 == result2

    def test_generate_creates_output_directory(self, tmp_path):
        """TTSGenerator creates output directory if it does not exist."""
        from src.generator.tts_generator import TTSGenerator

        with patch("src.generator.tts_generator.get_minimax") as mock_minimax:
            mock_service = MagicMock()
            mock_service.text_to_speech = AsyncMock(return_value=b"audio")
            mock_minimax.return_value = mock_service

            new_dir = tmp_path / "nested" / "audio"
            TTSGenerator(output_dir=str(new_dir))

            assert new_dir.exists()
