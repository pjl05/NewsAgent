from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator

from src.agent.tools import search_rss_feeds, fetch_page_content, duckduckgo_search


class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    next_action: str | None


def create_news_agent() -> StateGraph:
    """创建新闻 Agent 图"""
    workflow = StateGraph(AgentState)

    workflow.add_node("searcher", _search_node)
    workflow.add_node("generator", _generate_node)

    workflow.set_entry_point("searcher")
    workflow.add_edge("searcher", "generator")
    workflow.add_edge("generator", END)

    return workflow.compile()


def _search_node(state: AgentState) -> AgentState:
    """搜索节点"""
    query = state["messages"][-1].content
    rss_sources = [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://rss.cnblogs.com/news/",
    ]
    search_results = search_rss_feeds.invoke(rss_sources)
    ddg_results = duckduckgo_search.invoke({"query": query, "num_results": 5})

    content = f"RSS results: {len(search_results)}, DDG results: {len(ddg_results)}"
    return {"messages": [AIMessage(content=content)], "next_action": None}


def _generate_node(state: AgentState) -> AgentState:
    """生成节点"""
    return {"messages": [AIMessage(content="[Generated content would appear here]")], "next_action": None}


news_agent = create_news_agent()