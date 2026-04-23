import pytest
import sys
from pathlib import Path

# 确保 src 在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_settings():
    """模拟设置"""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.database_url = "postgresql://test:test@localhost:5432/test"
    settings.redis_url = "redis://localhost:6379/0"
    settings.milvus_host = "localhost"
    settings.milvus_port = 19530
    settings.minimax_api_key = "sk-cp-lHExR1fbSDQw4QdwDIsLUZIOATAXcooBUnpKMXIIDBAsBvpadscNNqc5h634Og4GG-ru34cxokk-S0nh69eFSQ-4mzH1J7YSudQ3MCxmccvD-EA9nLDA4qs"
    settings.minimax_embedding_api_key = "sk-cc46a6f6615b4708a2c0c3d42b631123"
    settings.minimax_model = "MiniMax-M2.7"
    return settings
