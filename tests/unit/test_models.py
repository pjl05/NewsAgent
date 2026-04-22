"""单元测试 - 数据模型"""
import pytest
from datetime import datetime

from src.models.user import User
from src.models.content import Content
from src.models.interaction import Interaction


class TestUserModel:
    """User 模型测试"""

    def test_user_creation(self):
        """测试用户创建"""
        user = User(
            user_id="wx_test_123",
            subscriptions=["AI", "Tech"],
            embedding=[0.1] * 768,
        )
        assert user.user_id == "wx_test_123"
        assert len(user.subscriptions) == 2
        assert user.feedback == {}

    def test_user_default_values(self):
        """测试用户默认值"""
        user = User(user_id="wx_test_456")
        assert user.subscriptions == []
        assert user.embedding is None
        assert user.feedback == {}


class TestContentModel:
    """Content 模型测试"""

    def test_content_creation(self):
        """测试内容创建"""
        content = Content(
            content_id="c_001",
            title="AI Breakthrough",
            source="36kr",
            url="https://36kr.com/p/123",
        )
        assert content.content_id == "c_001"
        assert content.title == "AI Breakthrough"
        assert content.audio_url is None
        assert content.video_url is None

    def test_content_with_tags(self):
        """测试带标签的内容"""
        content = Content(
            content_id="c_002",
            title="Tech News",
            tags=["AI", "LLM", "Tech"],
        )
        assert len(content.tags) == 3
        assert "AI" in content.tags


class TestInteractionModel:
    """Interaction 模型测试"""

    def test_interaction_creation(self):
        """测试交互创建"""
        interaction = Interaction(
            user_id="wx_test_123",
            content_id="c_001",
            action="click",
        )
        assert interaction.user_id == "wx_test_123"
        assert interaction.action == "click"
        assert interaction.read_time == 0

    def test_interaction_with_read_time(self):
        """测试带阅读时长的交互"""
        interaction = Interaction(
            user_id="wx_test_123",
            content_id="c_001",
            action="read",
            read_time=120,
        )
        assert interaction.read_time == 120
