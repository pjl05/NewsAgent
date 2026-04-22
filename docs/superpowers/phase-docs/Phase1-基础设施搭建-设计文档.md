# Phase 1: 基础设施搭建

**阶段：** Phase 1
**工期：** 2-3 周
**日期：** 2026-04-22

---

## 1.1 阶段目标

搭建项目基础框架，包括：
1. Docker Compose 多服务编排
2. PostgreSQL / Redis / Milvus 数据层
3. LangGraph Agent 核心架构
4. MiniMax API 集成

**交付物：** 可运行的 LangGraph Agent，具备基础对话能力

---

## 1.2 技术架构

### 1.2.1 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
├───────────┬───────────┬───────────┬───────────┬─────────────┤
│    app    │    db     │   redis   │  milvus  │   etcd+minio│
│  (Python) │ (Postgres)│  (Redis)  │ (Vector) │   (Storage) │
├───────────┴───────────┴───────────┴──────────┴─────────────┤
│                    共享数据层                                │
│         PostgreSQL  │  Redis  │  Milvus                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2.2 技术选型

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11-slim | 运行时 |
| PostgreSQL | 15-alpine | 关系数据库 |
| Redis | 7-alpine | 缓存 |
| Milvus | 3.0.0 | 向量数据库 |
| etcd | v3.5.5 | Milvus 依赖 |
| MinIO | latest | 对象存储 |
| FastAPI | 0.104.0 | Web 框架 |
| LangGraph | 0.0.21 | Agent 编排 |
| Uvicorn | 0.24.0 | ASGI 服务器 |

---

## 1.3 目录结构

```
newsagent/
├── docker-compose.yml              # 5 服务编排
├── Dockerfile                      # Python 镜像
├── requirements.txt                # Python 依赖
├── .env.example                    # 环境变量模板
├── src/
│   ├── __init__.py
│   ├── config.py                  # Settings 配置类
│   ├── main.py                    # FastAPI 入口
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User SQLAlchemy 模型
│   │   ├── content.py             # Content SQLAlchemy 模型
│   │   └── interaction.py         # Interaction 模型
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py           # PostgreSQL 连接
│   │   ├── redis.py               # Redis 客户端
│   │   └── milvus.py              # Milvus 客户端
│   ├── services/
│   │   ├── __init__.py
│   │   └── minimax.py             # MiniMax API
│   └── agent/
│       ├── __init__.py
│       ├── graph.py               # LangGraph
│       ├── nodes.py               # Agent Nodes
│       ├── tools.py               # Agent Tools
│       └── memory.py              # Memory
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_models.py
    │   └── test_minimax.py
    └── integration/
        ├── __init__.py
        └── test_agent.py
```

---

## 1.4 核心模块设计

### 1.4.1 config.py

**职责：** 集中管理所有环境配置

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 数据库
    database_url: str = "postgresql://postgres:postgres@localhost:5432/newsagent"
    redis_url: str = "redis://localhost:6379/0"

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # MiniMax
    minimax_api_key: str = ""
    minimax_model: str = "abab6.5s-chat"

    # 微信
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 搜索
    serpapi_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**配置项说明：**

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `minimax_api_key` | MiniMax Dashboard | 必需 |
| `wechat_app_id` | 微信公众平台 | Phase 5 需要 |
| `wechat_app_secret` | 微信公众平台 | Phase 5 需要 |
| `serpapi_key` | SerpAPI | Phase 2 需要 |
| `database_url` | PostgreSQL | Docker Compose 自动设置 |
| `redis_url` | Redis | Docker Compose 自动设置 |

### 1.4.2 main.py

**职责：** FastAPI 应用入口，提供 Web API

```python
from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.graph import build_agent

app = FastAPI(title="NewsAgent", version="0.1.0")
agent = build_agent()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    """对话接口 - 接收用户消息，返回 Agent 回复"""
    result = agent.invoke({"user_message": req.message})
    return {"response": result["response"], "user_id": req.user_id}

@app.get("/health")
def health() -> dict:
    """健康检查"""
    return {"status": "ok", "service": "newsagent"}

@app.get("/")
def root() -> dict:
    return {"message": "NewsAgent API", "docs": "/docs"}
```

---

## 1.5 数据模型

### 1.5.1 User 模型

```python
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)           # 微信 OpenID
    subscriptions = Column(JSON, default=list)           # 订阅主题列表 ["AI", "Tech"]
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSON, nullable=True)              # 用户兴趣向量
    feedback = Column(JSON, default=dict)                # 反馈数据 {content_id: score}
```

### 1.5.2 Content 模型

```python
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Content(Base):
    """内容模型"""
    __tablename__ = "contents"

    content_id = Column(String, primary_key=True)       # 唯一标识
    title = Column(String, nullable=False)              # 标题
    source = Column(String)                              # 来源平台
    url = Column(String)                                # 原文链接
    published_at = Column(DateTime)                     # 发布时间
    summary = Column(Text, nullable=True)             # AI 生成的摘要
    tags = Column(JSON, default=list)                   # 标签 ["AI", "LLM"]
    embedding = Column(JSON, nullable=True)             # 内容向量
    audio_url = Column(String, nullable=True)        # TTS 音频路径
    video_url = Column(String, nullable=True)         # 视频路径
    like_count = Column(Integer, default=0)          # 点赞数
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 1.5.3 Interaction 模型

```python
class Interaction(Base):
    """用户交互记录"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)            # 用户 ID
    content_id = Column(String, nullable=False)         # 内容 ID
    action = Column(String, nullable=False)             # click/read/like/share/dislike
    read_time = Column(Integer, default=0)            # 阅读时长（秒）
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 1.6 LangGraph Agent 设计

### 1.6.1 Agent 状态

```python
class AgentState(Dict[str, Any]):
    user_message: str          # 用户输入消息
    intent: str = ""           # 意图 (search/chat/report)
    query: str = ""            # 查询内容
    context: list = []         # 检索到的上下文
    ranked_content: list = []   # 排序后的内容
    response: str = ""         # 最终回复
```

### 1.6.2 Agent 工作流

```
                    ┌──────────────┐
                    │   START      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  understand   │  理解用户意图
                    │   (node)     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌───▼────┐ ┌────▼─────┐
       │  search    │ │  chat  │ │ report   │  (条件分支)
       │  intent    │ │ intent │ │ intent   │
       └──────┬──────┘ └───┬────┘ └────┬─────┘
              │            │           │
              └────────────┼───────────┘
                           │
                    ┌──────▼───────┐
                    │  research    │  检索内容
                    │   (node)    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    rank      │  排序内容
                    │   (node)     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   generate   │  生成回复
                    │   (node)    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │     END      │
                    └──────────────┘
```

### 1.6.3 Node 实现

**understand_node:**
```python
def understand_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """解析用户意图"""
    message = state.get("user_message", "")

    # 意图判断
    if any(kw in message for kw in ["有什么", "查询", "推荐", "查看"]):
        intent = "search"
    elif any(kw in message for kw in ["周报", "总结", "每周"]):
        intent = "report"
    else:
        intent = "chat"

    return {"intent": intent, "query": message}
```

**research_node:**
```python
def research_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """基于意图检索内容"""
    # TODO: 实现真实检索逻辑
    return {"context": []}
```

**rank_node:**
```python
def rank_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """个性化排序"""
    # TODO: 实现真实排序逻辑
    return {"ranked_content": []}
```

**generate_node:**
```python
def generate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """生成回复"""
    return {"response": "我现在还在初始化中，完整功能即将上线。"}
```

---

## 1.7 数据库连接

### 1.7.1 PostgreSQL

```python
# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/newsagent",
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 1.7.2 Redis

```python
# src/db/redis.py
import redis
from typing import Optional

_redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    """获取 Redis 客户端（单例）"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url("redis://localhost:6379/0")
    return _redis_client
```

### 1.7.3 Milvus

```python
# src/db/milvus.py
from pymilvus import connections, Collection
from typing import Optional

_milvus_conn: Optional = None

def get_milvus():
    """获取 Milvus 连接"""
    global _milvus_conn
    if _milvus_conn is None:
        connections.connect(host="localhost", port="19530", alias="default")
    return connections
```

---

## 1.8 MiniMax API 集成

### 1.8.1 Chat API

```python
def minimax_chat(
    messages: List[Dict[str, str]],
    model: str = "abab6.5s-chat",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """调用 MiniMax 聊天 API"""
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    with httpx.Client() as client:
        response = client.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["messages"][0]["content"]
```

### 1.8.2 Embedding API

```python
def minimax_embedding(text: str) -> List[float]:
    """获取文本 Embedding 向量"""
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
        "Content-Type": "application/json"
    }
    payload = {"model": "emb-01", "texts": [text]}

    with httpx.Client() as client:
        response = client.post(
            "https://api.minimax.chat/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
```

### 1.8.3 TTS API

```python
def minimax_tts(text: str, voice: str = "male-qn") -> bytes:
    """文本转语音"""
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
    }
    payload = {"model": "speech-01", "text": text, "voice": voice}

    with httpx.Client() as client:
        response = client.post(
            "https://api.minimax.chat/v1/audio/speech",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        return response.content
```

---

## 1.9 测试策略

### 1.9.1 单元测试

**test_models.py:**
```python
def test_user_creation():
    user = User(
        user_id="wx_test_123",
        subscriptions=["AI", "Tech"],
        embedding=[0.1] * 768
    )
    assert user.user_id == "wx_test_123"
    assert len(user.subscriptions) == 2

def test_content_creation():
    content = Content(
        content_id="c_001",
        title="AI Breakthrough",
        source="36kr",
        url="https://36kr.com/p/123",
        embedding=[0.2] * 768
    )
    assert content.content_id == "c_001"
    assert content.audio_url is None
```

**test_minimax.py:**
```python
def test_minimax_chat():
    with patch("httpx.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"messages": [{"role": "assistant", "content": "test"}]}]
        }
        result = minimax_chat([{"role": "user", "content": "hello"}])
        assert "test" in str(result)
```

### 1.9.2 集成测试

**test_agent.py:**
```python
def test_understand_node():
    result = understand_node({"user_message": "昨天有什么AI新闻?"})
    assert "intent" in result
    assert result["intent"] == "search"
```

---

## 1.10 依赖关系

```
Phase 1 交付物:
├── docker-compose.yml  ← 基础编排
├── config.py          ← 配置层
├── models/            ← 数据模型
├── db/                ← 数据库连接
├── services/minimax.py ← API 集成
└── agent/             ← LangGraph Agent
                              ↓
                        Phase 2 依赖
                        Phase 3 依赖
                        Phase 4 依赖
```

---

## 1.11 验收标准

| 检查项 | 标准 |
|--------|------|
| Docker Compose | 5 个服务启动成功 |
| 数据库连接 | PostgreSQL / Redis / Milvus 连接正常 |
| API 响应 | GET /health 返回 {"status": "ok"} |
| Agent 对话 | POST /chat 有响应返回 |
| 测试通过率 | 单元测试 100% 通过 |
| 代码质量 | 无 Pylint 错误 |
