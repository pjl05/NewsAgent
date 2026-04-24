from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel

from src.db.database import init_db, get_db
from src.db.redis import redis_client
from src.db.milvus import milvus_client
from src.agent.graph import news_agent
from src.services.minimax import get_minimax
from src.worker.tasks import collect_rss, collect_platforms
from src.recommender.engine import RecommendationEngine
from src.recommender.collab import CollaborativeFilter
from src.recommender.embedder import ContentEmbedder


class QueryRequest(BaseModel):
    query: str
    user_id: str


class QueryResponse(BaseModel):
    result: str
    audio_url: str | None = None


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
    import logging
    logger = logging.getLogger(__name__)
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