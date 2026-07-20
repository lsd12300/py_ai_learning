# -*- coding: utf-8 -*-
# 短期记忆

from dataclasses import dataclass, field
from typing import Literal


# 类型注解. 类似枚举, 限制只能是 system, user, assistant 中的一个
MessageRole = Literal["system", "user", "assistant"]

@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ShortTermMemory:
    """
    保存对话历史, 控制上限.
    system 消息永远保留; 超出上限时 删除最旧的非 system 消息.
    """
    max_messages: int = 20
    _messages: list[Message] = field(default_factory=list)

    
    def add(self, role: MessageRole, content: str) -> None:
        """添加消息到记忆中."""
        self._messages.append(Message(role, content))
        if len(self._messages) > self.max_messages:
            self._messages.pop(1)

    def _trim(self) -> None:
        """超出上限时 删除最旧的非 system 消息."""
        non_system = [msg for msg in self._messages if msg.role != "system"]
        while len(non_system) > self.max_messages:
            for i, msg in enumerate(self._messages):
                if msg.role != "system":
                    self._messages.pop(i)
                    break
            non_system = [msg for msg in self._messages if msg.role != "system"]

    def to_api_format(self) -> list[dict]:
        """转成 OpenAI API 需要的格式."""
        return [{"role": msg.role, "content": msg.content} for msg in self._messages]
    
    def clear_non_system(self) -> None:
        """清除对话历史 (保留 system 消息)."""
        self._messages = [msg for msg in self._messages if msg.role == "system"]

    def count(self) -> int:
        """返回对话历史中 非系统消息数量."""
        return len([msg for msg in self._messages if msg.role != "system"])
