# NewsAgent

AI 驱动个性化内容聚合平台。支持 RSS 订阅源 / 热搜采集、向量检索 + 协同过滤推荐、AI 内容生成（摘要 / TTS / 图表）、移动端 Web UI。

---

## 功能特性

| 模块 | 说明 |
|------|------|
| 内容采集 | RSS 源采集（36kr、虎嗅、少数派等）+ 微博/抖音/百度热搜 |
| 推荐引擎 | 内容向量 embedding + 用户向量协同过滤 |
| 内容生成 | AI 摘要（MiniMax）+ TTS 语音朗读 + 趋势/话题图表 |
| 移动端 UI | React + TailwindCSS + GSAP，暗色 Aurora 极光主题，玻璃拟态卡片 |
| 定时任务 | Celery Beat 自动化采集、embedding 生成、内容生成 |
| AI 对话 | 基于 LangGraph Agent 的自然语言查询界面 |

---

## 技术栈

**后端**
- Python 3.11 + FastAPI
- LangGraph（Agent 编排）
- Celery + Redis（任务队列）
- PostgreSQL（结构化数据）
- Milvus（向量数据库）
- MiniMax API（LLM + Embedding + TTS）

**前端**
- React 18 + TypeScript
- Vite + TailwindCSS
- Zustand（状态管理）
- GSAP（动画）

**部署**
- Docker Compose（PostgreSQL / Redis / Milvus / MinIO / FastAPI / Celery）

---

## 快速启动

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入必要密钥：

```env
# MiniMax API（必须）— https://platform.minimaxi.com/
MINIMAX_API_KEY=your_key_here
MINIMAX_EMBEDDING_API_KEY=your_key_here
MINIMAX_MODEL=MiniMax-M2.7

# 天履 API（热搜采集必需）— https://www.tianapi.com/
TIANAPI_KEY=your_key_here
```

### 2. 启动所有服务

```bash
docker compose up -d
```

等待所有服务健康（约 1-2 分钟）：

```bash
docker compose ps
# NAME                STATUS
# newsagent-app       healthy
# newsagent-db        healthy
# newsagent-redis     running
# newsagent-milvus    healthy
# newsagent-minio     healthy
```

### 3. 验证服务

```bash
# API 健康检查
curl http://localhost:8000/health
# {"status": "ok"}

# API 文档
# 浏览器打开 http://localhost:8000/docs
```

### 4. 手动触发首次数据采集

```bash
curl -X POST http://localhost:8000/admin/collect/rss
curl -X POST http://localhost:8000/admin/collect/platforms
```

### 5. 访问前端

```bash
cd newsagent/frontend
npm install
npm run dev
# 浏览器打开 http://localhost:5173
```

---

## 手机端访问（通过 Tailscale）

### PC 端
```bash
tailscale up
tailscale ip -4   # 记录返回的 IP，例如 100.x.x.x
```

### 手机端
1. 安装 Tailscale App，登录同一账号
2. 浏览器访问 `http://100.x.x.x:5173`

---

## 项目结构

```
newsagent/
├── frontend/                      # React 前端（移动端 Web UI）
│   ├── src/
│   │   ├── App.tsx               # 根组件 + Tab 路由
│   │   ├── components/
│   │   │   ├── aurora/           # AuroraBackground 极光背景
│   │   │   ├── ui/               # GlassCard/GlassInput/GlassNav/GlassButton
│   │   │   ├── feed/             # 精选 Feed（FeedPage/FeedList/FeedCard）
│   │   │   ├── search/           # 搜索（SearchPage/SearchResults）
│   │   │   ├── chat/             # AI 对话（ChatPage/ChatMessage/ChatInput）
│   │   │   ├── settings/         # 设置（SettingsPage/TopicSelector/TtsSettings）
│   │   │   └── player/           # TtsPlayer 底部播放器
│   │   ├── contexts/             # TtsPlayerContext 单例音频 Context
│   │   ├── hooks/               # useApi / useGsap
│   │   ├── stores/              # Zustand 全局状态（Tab/TTS/订阅/音色）
│   │   └── lib/                 # Axios API 客户端
│   └── tests/e2e/               # Playwright E2E 测试
│
src/                              # Python 后端
├── main.py                       # FastAPI 入口，所有 API 端点
├── config.py                     # Pydantic Settings（环境变量）
├── agent/
│   ├── graph.py                  # LangGraph Agent 定义
│   └── tools.py                  # Agent 可用工具
├── collector/
│   ├── rss_collector.py          # RSS 订阅源采集
│   ├── tianapi_collector.py      # 微博/抖音/百度热搜采集
│   ├── search_collector.py       # Bing/DuckDuckGo 搜索采集
│   └── dedup.py                  # 内容去重
├── recommender/
│   ├── embedder.py               # 内容向量 embedding（MiniMax）
│   ├── user_embedder.py          # 用户兴趣向量
│   ├── collab.py                 # 协同过滤（Jaccard 相似度）
│   ├── scorer.py                 # 综合评分（余弦相似度 + 新鲜度衰减）
│   └── engine.py                # 推荐引擎
├── generator/
│   ├── summarizer.py            # AI 摘要生成
│   ├── tts_generator.py          # TTS 语音生成
│   └── chart_generator.py       # 趋势图/话题分布图
├── db/
│   ├── database.py               # PostgreSQL（SQLAlchemy）
│   ├── redis.py                  # Redis 客户端
│   └── milvus.py                 # Milvus 向量数据库客户端
├── models/
│   ├── content.py                # Content 模型
│   ├── user.py                   # User 模型
│   └── interaction.py            # Interaction 模型（用户行为）
├── services/
│   └── minimax.py                # MiniMax API 封装（Chat/Embedding/TTS）
└── worker/
    ├── celery_app.py             # Celery Beat 调度器
    └── tasks.py                  # 所有 Celery Task

docker-compose.yml                # 全部服务编排
Dockerfile                        # Python 3.11 容器镜像
requirements.txt                  # Python 依赖
.env                              # 环境变量（密钥）
.env.example                      # 环境变量模板
```

---

## API 文档

基础 URL：`http://localhost:8000`

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/query` | POST | AI 聊天查询 |
| `/content/embed` | POST | 单条内容向量化入库 |
| `/content/search` | GET | 向量相似度搜索 |
| `/content/recommend` | GET | 个性化推荐（可选 user_id） |
| `/content/summarize` | POST | AI 生成摘要 |
| `/content/tts` | POST | 生成 TTS 音频 |
| `/content/chart/trend` | POST | 生成趋势折线图（PNG） |
| `/content/chart/topic` | POST | 生成话题分布饼图（PNG） |
| `/admin/collect/rss` | POST | 手动触发 RSS 采集 |
| `/admin/collect/platforms` | POST | 手动触发热搜采集 |

### 推荐请求示例

```bash
# 获取精选推荐（无用户 ID，使用 default）
curl "http://localhost:8000/content/recommend?top_k=20"

# 获取个性化推荐
curl "http://localhost:8000/content/recommend?user_id=user123&top_k=10"
```

### 搜索请求示例

```bash
curl -X POST "http://localhost:8000/content/search?query=AI&top_k=10"
```

### 生成摘要

```bash
curl -X POST http://localhost:8000/content/summarize \
  -H "Content-Type: application/json" \
  -d '{"content": "今日 AI 领域重要进展...", "max_words": 100}'
```

---

## 定时任务（Celery Beat）

所有任务时区：`Asia/Shanghai`

| 任务 | 时间 | 说明 |
|------|------|------|
| `collect-rss` | 每天 22:00 | 采集 RSS 订阅源 |
| `collect-platforms` | 每天 22:30 | 采集微博/抖音/百度热搜 |
| `daily-embedding` | 每天 23:00 | 为无向量内容生成 embedding |
| `daily-generation` | 每天 01:00 | 为无摘要内容生成摘要 + TTS |

---

## 前端开发

```bash
cd newsagent/frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# E2E 测试
npm run test:e2e
```

---

## 后端开发（本地）

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动 PostgreSQL / Redis / Milvus（通过 Docker）
docker compose up -d db redis milvus

# 启动 FastAPI
uvicorn src.main:app --reload --port 8000

# 启动 Celery Worker（新终端）
celery -A src.worker.celery_app worker --loglevel=info

# 启动 Celery Beat（新终端）
celery -A src.worker.celery_app beat --loglevel=info
```

---

## 测试

```bash
# Python 单元测试
pytest tests/unit/ -v

# 前端 TypeScript 类型检查
cd newsagent/frontend && npx tsc --noEmit

# 前端 E2E 测试（需要先启动服务）
cd newsagent/frontend && npx playwright test
```

---

## 环境变量说明

| 变量 | 必需 | 说明 |
|------|------|------|
| `MINIMAX_API_KEY` | 是 | MiniMax API 密钥（Chat + TTS） |
| `MINIMAX_EMBEDDING_API_KEY` | 是 | MiniMax Embedding API 密钥 |
| `MINIMAX_MODEL` | 否 | 模型名，默认 `MiniMax-M2.7` |
| `TIANAPI_KEY` | 是 | 天履 API 密钥（热搜采集） |
| `BING_API_KEY` | 否 | Bing 搜索 API（备用） |
