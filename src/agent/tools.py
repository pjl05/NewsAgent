from langchain_core.tools import tool
from typing import List, Dict, Any
import feedparser
import httpx
from bs4 import BeautifulSoup

from src.config import get_settings

settings = get_settings()


@tool
def search_rss_feeds(sources: List[str]) -> List[Dict[str, Any]]:
    """从 RSS 源获取内容"""
    results = []
    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                results.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", url),
                })
        except Exception:
            continue
    return results


@tool
def fetch_page_content(url: str) -> Dict[str, Any]:
    """获取网页内容"""
    try:
        response = httpx.get(url, timeout=10.0)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return {"url": url, "content": text[:2000]}
    except Exception as e:
        return {"url": url, "content": "", "error": str(e)}


@tool
def duckduckgo_search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """使用 DuckDuckGo 搜索"""
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://duckduckgo.com/html/?q={query}&kl=wt-wt"
    try:
        response = httpx.get(search_url, headers=headers, timeout=10.0)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for a in soup.select("a.result__a")[:num_results]:
            results.append({
                "title": a.get_text(),
                "url": a.get("href", ""),
            })
        return results
    except Exception:
        return []