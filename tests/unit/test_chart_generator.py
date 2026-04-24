"""Unit tests for the ChartGenerator class."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestChartGenerator:
    """Tests for ChartGenerator chart generation methods."""

    def test_generate_trend_chart_returns_bytes(self):
        """generate_trend_chart returns PNG image bytes."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_trend_chart(
            dates=["2024-01-01", "2024-01-02", "2024-01-03"],
            values=[10.0, 20.0, 15.0],
            title="测试趋势",
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_trend_chart_is_valid_png(self):
        """generate_trend_chart returns valid PNG data."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_trend_chart(
            dates=["2024-01-01", "2024-01-02"],
            values=[5.0, 10.0],
        )

        # PNG files start with PNG signature
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_generate_topic_distribution_returns_bytes(self):
        """generate_topic_distribution returns PNG image bytes."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_topic_distribution(
            topics={"科技": 30, "娱乐": 25, "体育": 45},
            title="话题分布",
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_topic_distribution_is_valid_png(self):
        """generate_topic_distribution returns valid PNG data."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_topic_distribution(
            topics={"A": 50, "B": 50},
        )

        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_generate_trend_chart_with_empty_data_returns_bytes(self):
        """Empty dates/values list still returns bytes."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_trend_chart(
            dates=[],
            values=[],
            title="空趋势",
        )

        assert isinstance(result, bytes)

    def test_generate_topic_distribution_with_empty_topics_returns_bytes(self):
        """Empty topics dict still returns bytes."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_topic_distribution(
            topics={},
            title="空分布",
        )

        assert isinstance(result, bytes)

    def test_generate_trend_chart_custom_title(self):
        """Custom title is accepted without error."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_trend_chart(
            dates=["2024-01-01", "2024-01-02"],
            values=[1.0, 2.0],
            title="自定义标题",
        )

        assert isinstance(result, bytes)

    def test_generate_topic_distribution_custom_title(self):
        """Custom title is accepted without error."""
        from src.generator.chart_generator import ChartGenerator

        chart_gen = ChartGenerator()
        result = chart_gen.generate_topic_distribution(
            topics={"X": 100},
            title="自定义标题",
        )

        assert isinstance(result, bytes)
