# Phase 4: 内容生成

**阶段：** Phase 4
**工期：** 2 周
**前置依赖：** Phase 1 + Phase 3

---

## 4.1 阶段目标

实现多模态内容生成，包括：
1. 文字摘要生成（MiniMax LLM）
2. TTS 语音生成（MiniMax TTS）
3. 视频生成（MiniMax Video API）
4. 每周报告生成
5. 可视化图表

**交付物：** 文字 + 音频 + 视频多模态内容生成管道

---

## 4.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    内容生成层 (Generator)                   │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Summarizer     │  TTSGenerator   │  VideoGenerator        │
│  (LLM 摘要)     │  (语音合成)      │  (视频生成)             │
└─────────────────┴─────────────────┴─────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    WeeklyReportGenerator                    │
│                    ChartGenerator                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4.3 核心模块设计

### 4.3.1 Summarizer

```python
from src.services.minimax import minimax_chat
from typing import List

class Summarizer:
    def __init__(self, model: str = "abab6.5s-chat"):
        self.model = model

    def summarize(self, content: str, max_words: int = 100) -> str:
        prompt = f"请用{max_words}字以内总结以下内容，要求简洁、有信息量：\n{content}\n摘要："
        messages = [{"role": "user", "content": prompt}]
        return minimax_chat(messages, model=self.model)
```

### 4.3.2 TTSGenerator

```python
from src.services.minimax import minimax_tts
from pathlib import Path
import hashlib

class TTSGenerator:
    def __init__(self, output_dir: str = "./data/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, text: str, voice: str = "male-qn") -> str:
        audio_bytes = minimax_tts(text, voice=voice)
        filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
        filepath = self.output_dir / filename
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        return str(filepath)
```

### 4.3.3 ChartGenerator

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Dict, List
from datetime import datetime

class ChartGenerator:
    def generate_trend_chart(self, dates, values, title="趋势图") -> bytes:
        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o')
        plt.title(title)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf.read()

    def generate_topic_distribution(self, topics: Dict[str, int]) -> bytes:
        plt.figure(figsize=(8, 8))
        plt.pie(list(topics.values()), labels=list(topics.keys()), autopct='%1.1f%%')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf.read()
```

---

## 4.4 验收标准

| 检查项 | 标准 |
|--------|------|
| 摘要生成 | 100 字内提取关键信息 |
| TTS 生成 | MP3 文件可播放 |
| 图表生成 | PNG 图片可读 |
