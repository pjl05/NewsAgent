from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel

from src.db.database import init_db, get_db
from src.db.redis import redis_client
from src.db.milvus import milvus_client
from src.agent.graph import news_agent
from src.services.minimax import get_minimax


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