import logging
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates chart images (PNG) using matplotlib."""

    def generate_trend_chart(
        self, dates: List[str], values: List[float], title: str = "趋势图"
    ) -> bytes:
        """Generate a line chart showing trends over time.

        Args:
            dates: List of date labels for the x-axis.
            values: List of numeric values for the y-axis.
            title: Chart title.

        Returns:
            PNG image bytes, or empty bytes on error.
        """
        try:
            plt.figure(figsize=(10, 5))
            plt.plot(dates, values, marker="o")
            plt.title(title)
            plt.xlabel("日期")
            plt.ylabel("值")
            plt.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            return buf.read()
        except Exception as e:
            logger.error("Failed to generate trend chart: %s", e)
            return b""

    def generate_topic_distribution(
        self, topics: Dict[str, int], title: str = "话题分布"
    ) -> bytes:
        """Generate a pie chart showing topic distribution.

        Args:
            topics: Dictionary mapping topic names to counts.
            title: Chart title.

        Returns:
            PNG image bytes, or empty bytes on error.
        """
        try:
            plt.figure(figsize=(8, 8))
            plt.pie(
                list(topics.values()),
                labels=list(topics.keys()),
                autopct="%1.1f%%",
            )
            plt.title(title)
            plt.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            return buf.read()
        except Exception as e:
            logger.error("Failed to generate topic distribution chart: %s", e)
            return b""
