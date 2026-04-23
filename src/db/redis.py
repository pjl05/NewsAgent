import redis.asyncio as redis
from typing import AsyncGenerator, Any
import json

from src.config import get_settings

settings = get_settings()


class RedisClient:
    """Redis 异步客户端封装"""

    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """建立 Redis 连接"""
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self) -> None:
        """关闭 Redis 连接"""
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> str | None:
        """获取值"""
        return await self._client.get(key) if self._client else None

    async def set(
        self,
        key: str,
        value: str,
        expire: int | None = None,
    ) -> None:
        """设置值，可选过期时间(秒)"""
        if self._client:
            if expire:
                await self._client.setex(key, expire, value)
            else:
                await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        """删除键"""
        if self._client:
            await self._client.delete(key)

    async def get_json(self, key: str) -> Any | None:
        """获取 JSON 格式的值"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: int | None = None,
    ) -> None:
        """设置 JSON 格式的值"""
        await self.set(key, json.dumps(value), expire)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self._client.exists(key) > 0 if self._client else False


# 全局单例
redis_client = RedisClient()


async def get_redis() -> AsyncGenerator[RedisClient, None]:
    """依赖注入用的生成器"""
    yield redis_client