import asyncio
import hashlib
import logging
from pathlib import Path

from src.services.minimax import get_minimax

logger = logging.getLogger(__name__)


class TTSGenerator:
    """Converts text to speech using MiniMax TTS API and saves to MP3 file."""

    def __init__(self, output_dir: str = "/app/data/audio") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, text: str, voice_id: str = "English_expressive_narrator") -> str:
        """
        Generate TTS audio from text and save to MP3 file.

        Args:
            text: The text content to convert to speech.
            voice_id: The voice ID to use for TTS generation.

        Returns:
            The file path of the generated MP3 file, or empty string on error.
        """
        try:
            minimax = get_minimax()
            audio_bytes = asyncio.run(minimax.text_to_speech(text, voice_id))

            filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
            filepath = self.output_dir / filename

            with open(filepath, "wb") as f:
                f.write(audio_bytes)

            logger.info("TTS generated successfully: %s", filepath)
            return str(filepath)

        except Exception as e:
            logger.error("TTS generation failed: %s", e)
            return ""