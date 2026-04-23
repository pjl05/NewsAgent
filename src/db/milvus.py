from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType
from typing import List

from src.config import get_settings

settings = get_settings()


class MilvusClientWrapper:
    """Milvus Lite 客户端封装（嵌入式模式）"""

    def __init__(self) -> None:
        self._client: MilvusClient | None = None
        self._collection_name = "content_embeddings"

    def connect(self, uri: str | None = None) -> None:
        """连接 Milvus（TCP 模式）"""
        uri = uri or "http://milvus:19530"
        self._client = MilvusClient(uri=uri)

        if not self._client.has_collection(self._collection_name):
            self.create_collection()

        self._client.load_collection(self._collection_name)

    def _ensure_loaded(self) -> None:
        """确保 collection 已加载到内存，避免搜索时报 not loaded 错误"""
        if self._client is None:
            raise RuntimeError("Milvus client not connected")

        try:
            stats = self._client.get_collection_stats(self._collection_name)
            state = stats.get("load_state", {}).get("state", "")
            if state != "Loaded":
                self._client.load_collection(self._collection_name)
        except Exception:
            self._client.load_collection(self._collection_name)

    def disconnect(self) -> None:
        """断开连接（Milvus Lite 无需断开）"""
        self._client = None

    def create_collection(self) -> None:
        """创建内容向量集合"""
        if self._client is None:
            raise RuntimeError("Milvus client not connected")

        if self._client.has_collection(self._collection_name):
            self._client.drop_collection(self._collection_name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
        ]
        schema = CollectionSchema(fields=fields, description="Content embeddings for NewsAgent")
        self._client.create_collection(
            collection_name=self._collection_name,
            schema=schema,
            metric_type="COSINE",
        )
        # 创建索引（前需要先建索引才能 load）
        index_params = self._client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )
        self._client.create_index(
            collection_name=self._collection_name,
            index_params=index_params,
        )
        self._client.load_collection(self._collection_name)

    def insert(
        self,
        content_id: str,
        title: str,
        embedding: List[float],
    ) -> None:
        """插入向量数据"""
        if self._client is None:
            raise RuntimeError("Milvus client not connected")

        self._client.insert(
            collection_name=self._collection_name,
            data=[
                {
                    "content_id": content_id,
                    "title": title,
                    "embedding": embedding,
                }
            ],
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
    ) -> List[dict]:
        """搜索相似向量"""
        if self._client is None:
            raise RuntimeError("Milvus client not connected")

        self._ensure_loaded()

        results = self._client.search(
            collection_name=self._collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=["content_id", "title"],
        )

        return [
            {
                "content_id": r["entity"]["content_id"],
                "title": r["entity"]["title"],
                "score": r["distance"],
            }
            for r in results[0]
        ]

    def delete_by_content_id(self, content_id: str) -> None:
        """根据 content_id 删除向量"""
        if self._client is None:
            raise RuntimeError("Milvus client not connected")

        results = self._client.query(
            collection_name=self._collection_name,
            filter=f'content_id == "{content_id}"',
            output_fields=["id"],
        )
        if results:
            ids = [r["id"] for r in results]
            self._client.delete(
                collection_name=self._collection_name,
                pks=ids,
            )


# 全局单例
milvus_client = MilvusClientWrapper()


def get_milvus() -> MilvusClientWrapper:
    """获取 Milvus 客户端实例"""
    return milvus_client