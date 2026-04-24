import logging
from typing import List, Dict, Any

from src.services.minimax import get_minimax

logger = logging.getLogger(__name__)


class ContentEmbedder:
    """Content embedding processor using MiniMax API."""

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for raw text.

        Args:
            text: Raw text string to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        minimax = get_minimax()
        return await minimax.get_embedding(text)

    async def embed_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Embed a content dict by combining title + summary.

        Args:
            content: Dict with 'title' and optional 'summary' fields.

        Returns:
            The same dict with an added 'embedding' field (List[float]).
            If embedding fails, the dict is returned unchanged.
        """
        title = content.get("title", "")
        summary = content.get("summary", "")

        if not title and not summary:
            logger.warning("Content has no title or summary, skipping embedding: %s", content.get("content_id", "unknown"))
            return content

        combined_text = f"{title} {summary}".strip()

        try:
            embedding = await self.embed_text(combined_text)
            result = {**content, "embedding": embedding}
            logger.info("Embedded content %s (vector dim=%d)", content.get("content_id", "unknown"), len(embedding))
            return result
        except Exception as e:
            logger.error("Failed to embed content %s: %s", content.get("content_id", "unknown"), e)
            return content

    async def embed_batch(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed a batch of content dicts.

        Args:
            contents: List of content dicts with 'title' and optional 'summary'.

        Returns:
            List of content dicts, each with an 'embedding' field added.
            Failures are logged and individual items are returned without embedding.
        """
        results = []
        for content in contents:
            embedded = await self.embed_content(content)
            results.append(embedded)
        return results