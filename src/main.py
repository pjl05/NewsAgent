from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import logging

from src.db.database import init_db, get_db
from src.db.redis import redis_client
from src.db.milvus import milvus_client
from src.agent.graph import news_agent
from src.services.minimax import get_minimax
from src.worker.tasks import collect_rss, collect_platforms
from src.recommender.engine import RecommendationEngine
from src.recommender.collab import CollaborativeFilter
from src.recommender.embedder import ContentEmbedder
from src.generator import Summarizer, TTSGenerator, ChartGenerator
from src.wechat import MessageHandler, ScheduledPusher, WeChatClient


class WeChatMessageRequest(BaseModel):
    openid: str
    content: str


class QueryRequest(BaseModel):
    query: str
    user_id: str


class QueryResponse(BaseModel):
    result: str
    audio_url: str | None = None


class SummarizeRequest(BaseModel):
    content: str
    max_words: int = 100


class TTSRequest(BaseModel):
    text: str
    voice_id: str = "English_expressive_narrator"


class TrendChartRequest(BaseModel):
    dates: List[str]
    values: List[float]
    title: str = "趋势图"


class TopicDistributionRequest(BaseModel):
    topics: Dict[str, int]
    title: str = "话题分布"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_db()
    await redis_client.connect()
    milvus_client.connect()
    yield
    await redis_client.close()
    milvus_client.disconnect()


app = FastAPI(title="NewsAgent API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query_news(req: QueryRequest):
    minimax = get_minimax()
    result = await minimax.chat([
        {"role": "user", "content": req.query}
    ])
    return QueryResponse(result=result)


@app.post("/content/embed")
async def embed_content(content_id: str, title: str, text: str):
    try:
        minimax = get_minimax()
        embedding = await minimax.get_embedding(text)
        milvus_client.insert(content_id, title, embedding)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("embed_content failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/content/search")
async def search_content(query: str, top_k: int = 10):
    try:
        minimax = get_minimax()
        query_embedding = await minimax.get_embedding(query)
        results = milvus_client.search(query_embedding, top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/admin/collect/rss")
async def trigger_rss_collection():
    """手动触发 RSS 采集任务"""
    result = collect_rss.delay()
    return {"task_id": result.id, "status": "queued"}


@app.post("/admin/collect/platforms")
async def trigger_platform_collection():
    """手动触发微博/知乎热搜采集"""
    result = collect_platforms.delay()
    return {"task_id": result.id, "status": "queued"}


@app.get("/content/recommend")
async def recommend_content(user_id: str, top_k: int = 20):
    """个性化推荐"""
    try:
        collab = CollaborativeFilter()
        collab.load_from_db(user_id)
        engine = RecommendationEngine(collab)
        results = engine.get_recommendations(user_id, top_k=top_k)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Phase 4: 内容生成 endpoints

logger = logging.getLogger(__name__)


@app.post("/content/summarize")
async def summarize_content(req: SummarizeRequest):
    """生成内容摘要"""
    try:
        summarizer = Summarizer()
        result = await summarizer.summarize(req.content, req.max_words)
        return {"summary": result}
    except Exception as e:
        logger.exception("summarize_content failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/content/tts")
async def generate_tts(req: TTSRequest):
    """生成TTS音频，返回音频文件URL"""
    try:
        tts_gen = TTSGenerator()
        filepath = tts_gen.generate(req.text, req.voice_id)
        if not filepath:
            raise HTTPException(status_code=500, detail="TTS generation failed")
        return {"audio_url": filepath}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("generate_tts failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/content/chart/trend")
async def chart_trend(req: TrendChartRequest):
    """生成趋势折线图"""
    try:
        chart_gen = ChartGenerator()
        image_bytes = chart_gen.generate_trend_chart(req.dates, req.values, req.title)
        return StreamingResponse(
            iter([image_bytes]),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={req.title}.png"},
        )
    except Exception as e:
        logger.exception("chart_trend failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/content/chart/topic")
async def chart_topic(req: TopicDistributionRequest):
    """生成话题分布饼图"""
    try:
        chart_gen = ChartGenerator()
        image_bytes = chart_gen.generate_topic_distribution(req.topics, req.title)
        return StreamingResponse(
            iter([image_bytes]),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={req.title}.png"},
        )
    except Exception as e:
        logger.exception("chart_topic failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# Phase 5: WeChat integration endpoints

@app.post("/wechat/send")
async def send_wechat_message(req: WeChatMessageRequest):
    """发送微信消息给指定用户"""
    try:
        client = WeChatClient()
        result = client.send_message(req.openid, req.content)
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.exception("send_wechat_message failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/wechat/handle")
async def handle_wechat_message(req: QueryRequest):
    """处理微信用户消息，返回Agent响应"""
    try:
        handler = MessageHandler()
        result = handler.handle(req.query, req.user_id)
        return {"result": result}
    except Exception as e:
        logger.exception("handle_wechat_message failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/wechat/push/daily")
async def push_daily():
    """手动触发每日推送"""
    try:
        pusher = ScheduledPusher()
        result = pusher.push_daily([])
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.exception("push_daily failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/wechat/push/weekly")
async def push_weekly():
    """手动触发每周推送"""
    try:
        pusher = ScheduledPusher()
        result = pusher.push_weekly([])
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.exception("push_weekly failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e