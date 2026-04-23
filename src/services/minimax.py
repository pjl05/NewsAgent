from typing import List, Dict, Any
import httpx

from src.config import get_settings

settings = get_settings()


class MiniMaxService:
    """MiniMax API 服务封装"""

    def __init__(self) -> None:
        self.api_key = settings.minimax_api_key
        self.model = settings.minimax_model
        self.base_url = "https://api.minimax.chat/v1"

    async def get_embedding(self, text: str) -> List[float]:
        """获取文本 embedding（使用阿里云百炼）"""
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
        embedding_key = settings.minimax_embedding_api_key
        headers = {
            "Authorization": f"Bearer {embedding_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "text-embedding-v1",
            "input": text,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            if response.status_code != 200:
                raise Exception(f"Alibaba embedding API error {response.status_code}: {response.text}")
            data = response.json()
            embedding_list = data.get("data")
            if not embedding_list or not isinstance(embedding_list, list):
                raise Exception(f"Invalid embedding response: {data}")
            embedding = embedding_list[0].get("embedding")
            if not embedding or not isinstance(embedding, list):
                raise Exception(f"Embedding field missing or invalid: {data}")
            return embedding

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """对话生成"""
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            data = response.json()

            # 检查 API 返回是否正常
            if response.status_code != 200:
                raise Exception(f"MiniMax API error {response.status_code}: {data}")

            choices = data.get("choices")
            if not choices or len(choices) == 0:
                raise Exception(f"MiniMax API returned no choices: {data}")

            return choices[0].get("message", {}).get("content", "")

    async def text_to_speech(self, text: str, voice_id: str = "English_expressive_narrator") -> bytes:
        """文字转语音"""
        url = f"{self.base_url}/t2a_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "speech-2.8-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": 1,
                "vol": 1,
                "pitch": 0,
            },
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            return response.content


minimax_service = MiniMaxService()


def get_minimax() -> MiniMaxService:
    """获取 MiniMax 服务实例"""
    return minimax_service