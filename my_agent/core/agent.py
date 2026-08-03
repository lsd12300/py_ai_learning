# -*- coding: utf-8 -*-
# Agent基类


from typing import Optional
from abc import ABC, abstractmethod
from config import AgentConfig
from datetime import datetime


class Agent(ABC):
    """Agent基类"""

    def __init__(self, config: Optional[AgentConfig] = None):
        """初始化Agent"""
        self.config = config or AgentConfig.from_env()
        self._init_system_prompt()

    @abstractmethod
    def _init_system_prompt(self):
        """初始化系统提示"""
        pass

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().strftime(self.config.timestamp_format)

    @abstractmethod
    def run_task(self, task: str) -> str:
        """执行任务"""
        pass
