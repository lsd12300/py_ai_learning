# -*- coding: utf-8 -*-
"""
记忆系统基础类:
- MemoryItem: 记忆项数据结构
- MemoryConfig: 记忆系统配置
- BaseMemory: 记忆基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class MemoryItem(BaseModel):
    """记忆项数据结构"""
    id: str
    content: str
    memory_type: str
    user_id: str
    timestamp: datetime
    importance: float = 0.5
    metadate: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class MemoryConfig(BaseModel):
    """记忆系统配置"""
    
    # 存储路径
    storage_path: str = "./memory_data"

    # 统计用的基础配置
    max_capacity: int = 100
    importance_threshold: float = 0.1
    decay_factor: float = 0.95

    # 工作记忆特定配置
    working_memory_capacity: int = 10
    working_memory_tokens: int = 2000
    working_memory_ttl_minutes: float = 120  # ttl (Time-to Live)

    # 感知记忆特定配置
    perception_memory_modalities: List[str] = ["text", "image", "audio", "video"]



class BaseMemory(ABC):
    """记忆基类
    
    定义所有记忆类型的通用接口和行为"""
    
    def __init__(self, config: MemoryConfig, storage_backend = None):
        self.config = config
        self.storage_backend = storage_backend
        self.memory_type = self.__class__.__name__.lower().replace("memory", "")

    
    @abstractmethod
    def add(self, memory_item: MemoryItem) -> str:
        """
        添加记忆项
        
        Args:
            memory_item: 要添加的记忆项
        
        Returns:
            str: 记忆项ID
        """
        pass


    @abstractmethod
    def retrieve(self, query: str, limit: int = 5, **kwargs) -> List[MemoryItem]:
        """
        检索相关记忆
        
        Args:
            query: 查询内容
            limit: 返回数量限制
            **kwargs: 其他检索参数
        
        Returns:
            List[MemoryItem]: 相关记忆项列表
        """
        pass


    @abstractmethod
    def update(self, memory_id: str, content: str = None, importance: float = None, metadate: Dict[str, Any] = None) -> bool:
        """
        更新记忆项
        
        Args:
            memory_id: 记忆项ID
            content: 新内容
            importance: 新重要性
            metadate: 新元数据
        
        Returns:
            bool: 是否成功更新
        """
        pass


    @abstractmethod
    def remove(self, memory_id: str) -> bool:
        """
        删除记忆项
        
        Args:
            memory_id: 记忆项ID
        
        Returns:
            bool: 是否成功删除
        """
        pass

    @abstractmethod
    def has_memory(self, memory_id: str) -> bool:
        """
        检查记忆项是否存在
        
        Args:
            memory_id: 记忆项ID
        
        Returns:
            bool: 是否存在
        """
        pass


    @abstractmethod
    def clear(self) -> None:
        """
        清空所有记忆项
        """
        pass


    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        获取记忆系统统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        pass


    def _generate_id(self) -> str:
        """生成记忆项ID"""
        import uuid
        return str(uuid.uuid4())
    

    def _calculate_importance(self, content: str, base_importance: float = 0.5) -> float:
        """
        计算记忆项的重要性
        
        Args:
            content: 记忆项内容
            base_importance: 基础重要性值
        
        Returns:
            float: 计忆项的重要性分数
        """
        importance = base_importance

        # 基于内容长度
        if len(content) > 100:
            importance += 0.1

        # 基于关键词
        important_keywords = ["重要", "关键", "必须", "注意", "警告", "错误"]
        if any(keyword in content for keyword in important_keywords):
            importance += 0.2

        return max(0.0, min(1.0, importance))
    

    def __str__(self) -> str:
        stats = self.get_stats()
        return f"{self.__class__.__name__}(count={stats.get('count', 0)})"
    
    def __repr__(self) -> str:
        return self.__str__()
