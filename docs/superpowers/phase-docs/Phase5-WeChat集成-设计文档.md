# Phase 5: WeChat 集成

**阶段：** Phase 5
**工期：** 2 周
**前置依赖：** Phase 1 + Phase 4

---

## 5.1 阶段目标

实现微信消息处理和定时推送，包括：
1. 微信 API 客户端封装
2. 消息处理器
3. 定时推送服务
4. 消息模板配置

**交付物：** 微信端可用的对话式 Agent

---

## 5.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    微信消息处理层 (Bot)                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│  WeChatClient   │ MessageHandler   │  ScheduledPusher        │
│  (API 封装)     │  (消息处理)       │  (定时推送)              │
└─────────────────┴─────────────────┴─────────────────────────┘
```

---

## 5.3 核心模块设计

### 5.3.1 WeChatClient

```python
import httpx
from typing import Dict, Any, Optional
from src.config import get_settings

settings = get_settings()

class WeChatClient:
    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret
        self.access_token: Optional[str] = None
        self.base_url = "https://api.weixin.qq.com/cgi-bin"

    def get_access_token(self) -> str:
        if self.access_token:
            return self.access_token
        url = f"{self.base_url}/token"
        params = {"grant_type": "client_credential", "appid": self.app_id, "secret": self.app_secret}
        with httpx.Client() as client:
            response = client.get(url, params=params)
            data = response.json()
            self.access_token = data.get("access_token", "")
        return self.access_token

    def send_message(self, openid: str, content: str) -> Dict[str, Any]:
        token = self.get_access_token()
        url = f"{self.base_url}/message/custom/send?access_token={token}"
        payload = {"touser": openid, "msgtype": "text", "text": {"content": content}}
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            return response.json()
```

### 5.3.2 MessageHandler

```python
from src.agent.graph import build_agent

class MessageHandler:
    COMMANDS = {
        "今日内容": "_get_daily_summary",
        "今天有什么": "_get_daily_summary",
        "日报": "_get_daily_summary",
        "周报": "_get_weekly_report",
        "每周总结": "_get_weekly_report",
    }

    def __init__(self):
        self.agent = build_agent()

    def handle(self, message: str, user_id: str) -> str:
        command = self._check_command(message)
        if command:
            return getattr(self, command)(user_id)
        result = self.agent.invoke({"user_message": message})
        return result.get("response", "抱歉，我现在无法回答这个问题。")

    def _check_command(self, message: str) -> str:
        return self.COMMANDS.get(message)

    def _get_daily_summary(self, user_id: str) -> str:
        return "今日摘要：\n1. [AI突破] OpenAI发布新模型...\n2. [科技股] 英伟达财报超预期..."

    def _get_weekly_report(self, user_id: str) -> str:
        return "周报功能开发中，即将上线。"
```

### 5.3.3 ScheduledPusher

```python
from typing import List
from .wechat import WeChatClient
from .handler import MessageHandler

class ScheduledPusher:
    def __init__(self):
        self.wechat = WeChatClient()
        self.handler = MessageHandler()

    def push_daily(self, user_ids: List[str]) -> dict:
        for user_id in user_ids:
            summary = self.handler._get_daily_summary(user_id)
            self.wechat.send_message(user_id, summary)

    def push_weekly(self, user_ids: List[str]) -> dict:
        for user_id in user_ids:
            report = self.handler._get_weekly_report(user_id)
            self.wechat.send_message(user_id, report)
```

---

## 5.4 验收标准

| 检查项 | 标准 |
|--------|------|
| Access Token | 正确获取并缓存 |
| 消息发送 | 能发送给指定用户 |
| 命令响应 | 日报/周报命令正确响应 |
| 定时推送 | 定时任务正常触发 |
