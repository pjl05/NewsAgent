# NewsAgent 项目总结

**项目名称：** NewsAgent — 自动化新闻采集与个性化推送平台
**技术栈：** Python 3.12 / FastAPI / Celery / PostgreSQL / Redis / Milvus / MiniMax API
**部署：** Docker Compose 多服务编排
**代码仓库：** https://github.com/pjl05/NewsAgent
**最后更新：** 2026-04-24

---

## 一、项目概述

NewsAgent 是一个自动化新闻采集与个性化推送平台，支持：
- 多源内容采集（RSS、热搜、搜索引擎）
- 个性化推荐（Embedding + 协同过滤）
- 多模态内容生成（摘要、TTS、图表）
- 微信消息推送与定时日报/周报

---

## 二、已完成 Phases

| Phase | 内容 | 状态 | 关键文件 |
|-------|------|------|---------|
| 1 | 基础设施 | ✅ 完成 | `docker-compose.yml`, `src/config.py`, `src/models/`, `src/db/`, `src/services/minimax.py` |
| 2 | 内容采集 | ✅ 完成 | `src/collector/`, `src/worker/tasks.py` |
| 3 | 个性化推荐 | ✅ 完成 | `src/recommender/` |
| 4 | 内容生成 | ⚠️ 部分 | `src/generator/`（缺视频生成、周报生成） |
| 5 | WeChat 集成 | ⚠️ 单向 | `src/wechat/`（只能推送，无法自动接收回复） |
| 6 | 定时任务 | ✅ 完成 | `src/worker/celery_app.py` |

---

## 三、已实现功能详解

### 3.1 内容采集（Phase 2）

**采集来源：**
- RSS 源：36kr、虎嗅、少数派等
- 热搜：微博/抖音/百度（TianAPI，每天 100 次免费）
- 搜索：Bing / DuckDuckGo 补充采集

**数据流：**
```
Celery Beat (定时)
     │
     ├─ 22:00 collect_rss        → RSSCollector
     └─ 22:30 collect_platforms   → TianAPICollector (weibo/douyin/baidu)
                                    ↓
                              deduplicate_content()
                                    ↓
                              PostgreSQL (Content 表)
```

**关键文件：**
- `src/collector/rss_collector.py` — RSS 采集
- `src/collector/tianapi_collector.py` — 热搜采集
- `src/collector/search_collector.py` — 搜索采集
- `src/collector/dedup.py` — 内容去重
- `src/worker/tasks.py` — Celery 任务定义

---

### 3.2 个性化推荐（Phase 3）

**推荐算法：**
```
个性化得分 = α × cosine_similarity
          + β × collaborative_filter_score
          + γ × freshness_decay
          + δ × interaction_boost

α=0.5, β=0.2, γ=0.2, δ=0.1
```

**模块：**
- `src/recommender/embedder.py` — ContentEmbedder（MiniMax 向量化，1536 维）
- `src/recommender/user_embedder.py` — UserEmbedder（用户兴趣向量）
- `src/recommender/collab.py` — CollaborativeFilter（Jaccard 相似度）
- `src/recommender/scorer.py` — cosine_similarity + freshness_decay
- `src/recommender/engine.py` — RecommendationEngine

**API：** `GET /content/recommend?user_id=xxx&top_k=20`

---

### 3.3 内容生成（Phase 4）

| 模块 | 说明 | API |
|------|------|-----|
| Summarizer | LLM 摘要生成（最多 100 字） | `POST /content/summarize` |
| TTSGenerator | 文本转 MP3 | `POST /content/tts` |
| ChartGenerator | 趋势折线图 + 话题分布饼图 | `POST /content/chart/trend`, `/content/chart/topic` |

**缺失：**
- VideoGenerator（MiniMax 视频 API 未集成）
- WeeklyReportGenerator（周报聚合生成）

---

### 3.4 WeChat 集成（Phase 5）

**已实现模块：**
- `src/wechat/wechat_client.py` — WeChatClient（access_token 缓存、消息发送）
- `src/wechat/handler.py` — MessageHandler（命令路由：日报/周报 + Agent fallback）
- `src/wechat/scheduled_pusher.py` — ScheduledPusher（每日/每周推送）

**API：**
| 端点 | 说明 |
|------|------|
| `POST /wechat/send` | 发送消息给指定用户 |
| `POST /wechat/handle` | 处理用户消息（返回 Agent 响应） |
| `POST /wechat/push/daily` | 手动触发日报推送 |
| `POST /wechat/push/weekly` | 手动触发周报推送 |

---

### 3.5 定时任务（Phase 6）

**Celery Beat 调度表（Asia/Shanghai 时区）：**

| 时间 | 任务 | 说明 |
|------|------|------|
| 22:00 | `collect-rss-daily` | RSS 采集 |
| 22:30 | `collect-platforms-daily` | 微博/抖音/百度热搜 |
| 23:00 | `daily-embedding` | 为无向量的内容生成 embedding |
| 01:00 | `daily-generation` | 生成摘要 + TTS |
| 08:00 | `push-daily-summary` | 推送日报 |
| 周一 09:00 | `push-weekly-report` | 推送周报 |

---

## 四、完整 API 列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/query` | POST | MiniMax 对话 |
| `/content/embed` | POST | 内容向量化 |
| `/content/search` | GET | 向量检索 |
| `/content/recommend` | GET | 个性化推荐 |
| `/content/summarize` | POST | LLM 摘要生成 |
| `/content/tts` | POST | TTS 生成 |
| `/content/chart/trend` | POST | 趋势折线图 |
| `/content/chart/topic` | POST | 话题分布饼图 |
| `/admin/collect/rss` | POST | 手动触发 RSS 采集 |
| `/admin/collect/platforms` | POST | 手动触发热搜采集 |
| `/wechat/send` | POST | 发送微信消息 |
| `/wechat/handle` | POST | 处理微信消息 |
| `/wechat/push/daily` | POST | 手动推送日报 |
| `/wechat/push/weekly` | POST | 手动推送周报 |

---

## 五、数据模型

### 5.1 Content（内容）

| 字段 | 类型 | 说明 |
|------|------|------|
| content_id | String (PK) | 唯一标识 |
| title | String | 标题 |
| source | String | 来源平台 |
| url | String | 原文链接 |
| published_at | DateTime | 发布时间 |
| summary | Text | AI 摘要 |
| tags | JSON | 标签 |
| embedding | JSON | 向量（1536 维） |
| audio_url | String | TTS 音频路径 |
| like_count | Integer | 点赞数 |
| created_at | DateTime | 入库时间 |

### 5.2 User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | String (PK) | 微信 OpenID |
| subscriptions | JSON | 订阅主题列表 |
| embedding | JSON | 用户兴趣向量 |
| feedback | JSON | 反馈数据 |
| created_at | DateTime | 注册时间 |

### 5.3 Interaction（交互）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 自增 ID |
| user_id | String | 用户 ID |
| content_id | String | 内容 ID |
| action | String | click/read/like/share/dislike |
| read_time | Integer | 阅读时长（秒） |
| created_at | DateTime | 交互时间 |

---

## 六、Docker 服务架构

```
newsagent/
├── docker-compose.yml
├── app           — FastAPI 应用
├── db            — PostgreSQL 15
├── redis         — Redis 7
├── milvus        — 向量数据库 v2.4
├── minio         — 对象存储（S3 兼容）
└── etcd          — Milvus 依赖
```

---

## 七、缺失功能与待办

| 功能 | Phase | 优先级 | 说明 |
|------|-------|--------|------|
| 微信 Webhook 接收 | 5 | **高** | 需配置公众号服务器 URL，接收用户消息 |
| 消息加解密 | 5 | **高** | 微信消息体 AES PKCS7 加解密 |
| VideoGenerator | 4 | 中 | MiniMax 视频 API |
| WeeklyReportGenerator | 4 | 中 | 聚合一周内容生成报告 |
| 可视化报告推送 | 6 | 低 | 图表邮件/微信推送 |

---

## 八、敏感信息管理

- **`.env`** 文件存储所有密钥，已加入 `.gitignore`，永不提交
- `src/config.py` 中所有密钥默认为空字符串，强制从 `.env` 读取
- 历史提交中的硬编码密钥已通过 `git filter-branch` 清除
- 远程仓库已强制更新

---

## 九、开发规范

- Python 3.12，类型注解全覆盖
- 使用 `asyncio.run()` 包装 Celery 任务中的异步调用
- 错误处理：所有模块都有 try/except + logging
- 测试：单元测试 + E2E 测试（`tests/` 目录）
- 代码风格：PEP 8，不可变数据模式

---

## 十、快速开始

```bash
# 1. 配置 .env
cp .env.example .env
# 填写 MINIMAX_API_KEY, TIANAPI_KEY, WECHAT_APP_ID, WECHAT_APP_SECRET

# 2. 启动所有服务
docker compose up -d

# 3. 查看服务状态
docker compose ps

# 4. 查看 API 文档
open http://localhost:8000/docs

# 5. 手动触发采集
curl -X POST http://localhost:8000/admin/collect/rss
curl -X POST http://localhost:8000/admin/collect/platforms
```
