# -*- coding: utf-8 -*-
# 消息类. 用于上下文管理


from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel


# 消息角色类型
MessageRole = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    """消息类"""
    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(content=content, role=role, timestamp=kwargs.get("timestamp", datetime.now()), metadata=kwargs.get("metadata", {}))

    
    def to_dict(self):
        """将消息转换为字典. OpenAI 格式"""
        return {
            "content": self.content,
            "role": self.role
        }
    
    def __str__(self):
        return f"[{self.role}] {self.content}"
