"""集成测试 - Agent"""
import pytest

from src.agent.graph import AgentState, _search_node, _generate_node
from langchain_core.messages import HumanMessage


class TestAgentGraph:
    """Agent 图测试"""

    def test_search_node(self):
        """测试搜索节点"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content="有什么AI新闻")],
            "next_action": None,
        }

        # 注意：这个测试会真正调用 RSS/DDG，需要网络
        # 在 CI 环境中应该 mock
        result = _search_node(initial_state)

        assert "messages" in result
        assert len(result["messages"]) > 0
        assert result["next_action"] is None

    def test_generate_node(self):
        """测试生成节点"""
        state: AgentState = {
            "messages": [HumanMessage(content="test")],
            "next_action": None,
        }

        result = _generate_node(state)

        assert "messages" in result
        assert result["next_action"] is None
