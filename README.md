# NewsAgent

AI-powered personal content aggregation agent with WeChat delivery.

## Architecture

- **Agent Framework**: LangGraph
- **LLM/Embedding/TTS**: MiniMax API
- **Vector DB**: Milvus
- **RDBMS**: PostgreSQL
- **Cache**: Redis
- **Deployment**: Docker Compose

## Quick Start

```bash
docker-compose up -d
```

## API

- `GET /health` - Health check
- `POST /query` - Query news
- `POST /content/embed` - Embed content
- `GET /content/search` - Search content