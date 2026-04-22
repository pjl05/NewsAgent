# Phase 3: 个性化推荐

**阶段：** Phase 3
**工期：** 3 周
**前置依赖：** Phase 1 + Phase 2

---

## 3.1 阶段目标

实现个性化推荐引擎，包括：
1. 内容 Embedding 生成（MiniMax API）
2. 用户兴趣向量构建
3. 个性化排序算法
4. 协同过滤推荐

**交付物：** 个性化推荐引擎，根据用户兴趣和历史行为推荐内容

---

## 3.2 技术架构

### 3.2.1 推荐系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     推荐引擎 (Recommender)                  │
├─────────────────┬─────────────────┬─────────────────────┤
│ 内容 Embedding │ 用户兴趣建模     │ 排序算法             │
│                 │                 │                      │
│ • title+summary │ • 订阅主题      │ • cosine similarity  │
│ • MiniMax emb   │ • 交互历史       │ • collab filtering   │
│ • 128/768 维    │ • 反馈数据       │ • freshness decay    │
└─────────────────┴─────────────────┴─────────────────────┘
```

### 3.2.2 推荐算法核心公式

```
个性化得分 = α × cosine_similarity(user_embedding, content_embedding)
          + β × collaborative_filter_score
          + γ × freshness_decay
          + δ × interaction_boost

参数配置（初期）：
- α = 0.5 (内容-用户相似度主导)
- β = 0.2 (协同过滤)
- γ = 0.2 (新鲜度衰减)
- δ = 0.1 (交互信号增强)
```

---

## 3.3 核心模块设计

### 3.3.1 ContentEmbedder

```python
from src.services.minimax import minimax_embedding as api_embedding
from typing import List

class ContentEmbedder:
    """内容向量化处理器"""

    def embed(self, text: str) -> List[float]:
        """生成文本 Embedding 向量"""
        return api_embedding(text)
```

### 3.3.2 cosine_similarity

```python
import numpy as np
from typing import List

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """计算两个向量的余弦相似度"""
    a = np.array(a)
    b = np.array(b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))
```

### 3.3.3 calculate_score

```python
def calculate_score(
    user_embedding: List[float],
    content_embedding: List[float],
    collab_score: float,
    freshness: float,
    interaction_boost: float,
    alpha: float = 0.5,
    beta: float = 0.2,
    gamma: float = 0.2,
    delta: float = 0.1
) -> float:
    """计算内容个性化得分"""
    similarity = cosine_similarity(user_embedding, content_embedding)
    score = (alpha * similarity +
             beta * collab_score +
             gamma * freshness +
             delta * interaction_boost)
    return max(0.0, min(1.0, score))
```

### 3.3.4 CollaborativeFilter

```python
from typing import Dict, List, Tuple
from collections import defaultdict

class CollaborativeFilter:
    """基于用户行为的协同过滤推荐"""

    def __init__(self):
        self.user_item_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)

    def add_interaction(self, user_id: str, content_id: str, weight: float):
        """添加用户交互记录"""
        self.user_item_matrix[user_id][content_id] = weight

    def get_similar_users(self, user_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """查找与目标用户相似的用户（Jaccard 相似度）"""
        if user_id not in self.user_item_matrix:
            return []
        target_items = self.user_item_matrix[user_id]
        similarities = []
        for other_user, items in self.user_item_matrix.items():
            if other_user == user_id:
                continue
            intersection = set(target_items.keys()) & set(items.keys())
            union = set(target_items.keys()) | set(items.keys())
            if intersection:
                sim = len(intersection) / len(union)
                similarities.append((other_user, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def predict(self, user_id: str, content_id: str) -> float:
        """预测用户对内容的评分"""
        similar_users = self.get_similar_users(user_id)
        if not similar_users:
            return 0.0
        numerator = 0.0
        denominator = 0.0
        for other_user, sim in similar_users:
            if content_id in self.user_item_matrix[other_user]:
                rating = self.user_item_matrix[other_user][content_id]
                numerator += sim * rating
                denominator += sim
        return numerator / denominator if denominator > 0 else 0.0
```

### 3.3.5 RecommendationEngine

```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from .scorer import calculate_score
from .collab import CollaborativeFilter

class RecommendationEngine:
    """个性化推荐引擎"""

    def __init__(self, collab_filter: CollaborativeFilter):
        self.collab = collab_filter
        self.alpha = 0.5
        self.beta = 0.2
        self.gamma = 0.2
        self.delta = 0.1

    def rank(
        self,
        user_embedding: List[float],
        contents: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """对内容列表进行个性化排序"""
        now = datetime.utcnow()
        scored_contents = []

        for content in contents:
            published_at = content.get("published_at", now)
            age_days = max(0, (now - published_at).days)
            freshness = max(0.0, 1.0 - (age_days * 0.1))
            like_count = content.get("like_count", 0)
            interaction_boost = min(1.0, like_count / 100.0)
            collab_score = 0.0
            if user_id:
                content_id = content.get("content_id")
                if content_id:
                    collab_score = self.collab.predict(user_id, content_id)

            score = calculate_score(
                user_embedding=user_embedding,
                content_embedding=content.get("embedding", [0.0] * 128),
                collab_score=collab_score,
                freshness=freshness,
                interaction_boost=interaction_boost,
                alpha=self.alpha, beta=self.beta, gamma=self.gamma, delta=self.delta
            )
            scored_contents.append((score, content))

        scored_contents.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scored_contents[:top_k]]
```

---

## 3.4 验收标准

| 检查项 | 标准 |
|--------|------|
| Embedding 生成 | MiniMax API 返回正确维度向量 |
| 相似度计算 | cosine([1,0,0], [1,0,0]) = 1.0 |
| 协同过滤 | 能基于历史交互找到相似用户 |
| 排序引擎 | 返回结果按得分降序排列 |
| 测试 | 单元测试 100% 通过 |

---

## 3.5 依赖关系

```
Phase 2 ──→ Phase 3
              │
              ├─→ services/minimax.py (Embedding API)
              ├─→ models/content.py (内容向量存储)
              └─→ models/interaction.py (交互数据)
```
