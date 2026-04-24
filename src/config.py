from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@db:5432/newsagent"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/1"
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    minimax_api_key: str = ""
    minimax_embedding_api_key: str = ""
    minimax_model: str = "MiniMax-M2.7"
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    bing_api_key: str = ""
    tianapi_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
