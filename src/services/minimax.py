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
        """获取文本 embedding"""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "embo-01",
            "text": text,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            data = response.json()
            return data.get("data", [{}])[0].get("embedding", [])

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
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def text_to_speech(self, text: str, voice: str = "male-qn") -> bytes:
        """文字转语音"""
        url = f"{self.base_url}/t2a_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "speech-01",
            "text": text,
            "voice_setting": voice,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            return response.content


minimax_service = MiniMaxService()


def get_minimax() -> MiniMaxService:
    """获取 MiniMax 服务实例"""
    return minimax_service