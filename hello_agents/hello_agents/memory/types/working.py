# -*- coding: utf-8 -*-
"""
工作记忆:
- 短期上下文管理
- 容量和时间限制
- 优先级管理
- 自动清理
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import heapq

from ..base import BaseMemory, MemoryItem, MemoryConfig


class WorkingMemory(BaseMemory):
    """
    工作记忆

    特点:
    - 容量有限(10-20条)
    - 时效性强(会话级别)
    - 优先级管理
    - 自动清理(过期)
    """

    def __init__(self, config: MemoryConfig, storage_backend:None):
        super().__init__(config, storage_backend)

        # 工作记忆特定配置
        self.max_capacity = self.config.working_memory_capacity
        self.max_tokens = self.config.working_memory_tokens
        # 纯内存TTL（分钟），可通过在 MemoryConfig 上挂载 working_memory_ttl_minutes 覆盖
        self.max_age_minutes = getattr(self.config, "working_memory_ttl_minutes", 120)
        self.current_tokens = 0
        self.session_start = datetime.now()

        # 内存存储 (工作记忆不需要持久化)
        self.memories: List[MemoryItem] = []

        # 优先级队列 (按重要性排序)
        self.memory_heap = []  # (priority, timestamp, memory_item)


    def add(self, memory_item: MemoryItem) -> str:
        """添加记忆项"""
        # 过期清理
        self._expire_old_memories()
        # 计算新记忆项的优先级
        priority = self._calculate_priority(memory_item)

        # 入堆
        heapq.heappush(self.memory_heap, (-priority, memory_item.timestamp, memory_item))
        self.memories.append(memory_item)

        # 更新 token计数
        self.current_tokens += len(memory_item.content.split())

        # 检查容量限制
        self._enforce_capacity_limits()

        return memory_item.id
    

    def retrieve(self, query: str, limit: int = 5, user_id: str = None, **kwargs) -> List[MemoryItem]:
        """检索记忆项 - 混合语义向量检索和关键词匹配"""
        # 过期清理
        self._expire_old_memories()
        if not self.memories:
            return []
        
        # 过滤已遗忘记忆
        active_memories = [m for m in self.memories if not m.metadate.get("forgotten", False)]

        # 按用户ID过滤
        filtered_memories = active_memories
        if user_id:
            filtered_memories = [m for m in filtered_memories if m.user_id == user_id]

        if not filtered_memories:
            return []
        
        # 尝试语义向量检索 (如果有 嵌入模型)
        vector_scores = {}
        try:
            # 简单的语义相似度计算 (TF-IDF)
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np

            # 准备文档
            documents = [query] + [m.content for m in filtered_memories]

            # TF-IDF向量化
            vectorizer = TfidfVectorizer(stop_words=None, lowercase=True)
            tfidf_matrix = vectorizer.fit_transform(documents)

            # 计算相似度
            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            similarities = cosine_similarity(query_vec, doc_vecs).flatten()

            # 存储向量分数
            for i, memory in enumerate(filtered_memories):
                vector_scores[memory.id] = similarities[i]

        except Exception as e:
            # 向量检索失败, 回退关键词匹配
            vector_scores = {}

        # 计算最终分数
        query_lower = query.lower()
        scored_memories = []
        for memory in filtered_memories:
            content_lower = memory.content.lower()

            # 获取向量分数
            vector_score = vector_scores.get(memory.id, 0.0)

            # 关键词分数
        heapq.heapify(scored_memories)
        heapq.nlargest(limit, scored_memories, key=lambda x: x[1])
        return [m for m, s in heapq.nlargest(limit, scored_memories, key=lambda x: x[1])]
       


    
    def _expire_old_memories(self):
        """过期旧记忆项"""
        pass

    def _calculate_priority(self, memory_item: MemoryItem) -> float:
        """计算记忆项的优先级"""
        pass

    def _enforce_capacity_limits(self):
        """强制执行容量限制"""
        pass

        
