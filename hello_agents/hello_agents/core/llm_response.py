# -*- coding: utf-8 -*-
# LLM响应类

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """统一的工具调用对象"""
    id: str
    name: str
    arguments: str


@dataclass
class LLMToolResponse:
    """统一的LLM工具调用响应对象"""
    content: Optional[str]
    tool_calls: List[ToolCall]
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0


@dataclass
class LLMResponse:
    """
    统一的LLM响应对象
    包含模型的响应内容, 推理过程, token统计, 响应耗时
    :param content: 模型的响应内容
    :param model: 模型ID
    :param usage: Token使用统计: {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
    :param latency_ms: 响应耗时, 单位毫秒
    :param reasoning_content: 推理过程内容(仅 thinking 模型有)
    """
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0
    reasoning_content: Optional[str] = None


    def __str__(self):
        """向后兼容, 返回模型的响应内容"""
        return self.content
    
    def __repr__(self):
        """详细信息展示"""
        parts = [
            f"LLMResponse(model={self.model}",
            f"latency={self.latency_ms}ms",
            f"tokens={self.usage.get('total_tokens', 0)}",
        ]
        if self.reasoning_content:
            parts.append(f"has_reasoning=True")
        parts.append(f"content_length={len(self.content)})")
        return ", ".join(parts)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
        }
        if self.reasoning_content:
            result["reasoning_content"] = self.reasoning_content
        return result



@dataclass
class StreamStats:
    """
    流式响应统计信息
    """
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0
    reasoning_content: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "model": self.model,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
        }
        if self.reasoning_content:
            result["reasoning_content"] = self.reasoning_content
        return result
