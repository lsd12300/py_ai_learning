# -*- coding: utf-8 -*-
# Agent 状态栏


import sys
import os
import platform
from typing import Optional
from core.agent import Agent
from my_agent.core.config import Config


class SystemHintAgent(Agent):
    """Agent 状态栏"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.current_directory = os.getcwd()    # 当前工作目录
        self.conversation_history = []  # 对话历史记录(即 上下文)

        self._init_system_prompt()


    def _init_system_prompt(self):
        """初始化系统提示. 提醒关注和更新状态栏信息"""
        system_content = """You are an intelligent assistant with access to various tools for file operations, code execution, and system commands.

Your task is to complete the given objectives efficiently using the available tools. Think step by step and use tools as needed.

## TODO List Management Rules:
- For any complex task with 3+ distinct steps, immediately create a TODO list using `rewrite_todo_list`
- Break down the user's request into specific, actionable TODO items
- Update TODO items to 'in_progress' when starting work on them using `update_todo_status`
- Mark items as 'completed' immediately after finishing them
- Only have ONE item 'in_progress' at a time
- If you encounter errors or need to change approach, update relevant TODOs to 'cancelled' and add new ones
- Use the TODO list as your primary planning and tracking mechanism
- Reference TODO items by their ID when discussing progress

## Key Behaviors:
1. ALWAYS start complex tasks by creating a TODO list
2. Pay attention to timestamps to understand the timeline of events
3. Notice tool call numbers (e.g., "Tool call #3") to avoid repetitive loops - if you see high numbers, change strategy
4. Learn from detailed error messages to fix issues and adapt your approach
5. Be aware of your current directory and system environment shown in system state
6. When exploring projects, systematically read key files (README, main.py, agent.py) to understand structure

## Error Handling:
- Read error messages carefully - they contain specific information about what went wrong
- Use the suggestions provided in error messages to fix issues
- If a tool fails multiple times (check the call number), try a different approach
- Common fixes: check file paths, verify current directory, ensure proper permissions

Important: When you have completed all tasks, clearly state "FINAL ANSWER:" followed by a comprehensive summary of what was accomplished."""

        self.conversation_history = [
            {"role": "system", "content": system_content}
        ]

    def _get_system_status(self) -> str:
        """获取系统状态信息"""
        if not self.config.enable_system_state:
            return ""

        # 不同平台的 Shell 类型不同
        system = platform.system()
        if system == "Windows":
            shell_type = "Windows Command Prompt or PowerShell"
        elif system == "Darwin":
            shell_type = "macOS Terminal (zsh/bash)"
        else:
            shell_type = f"Linux Shell ({os.environ.get('SHELL', 'bash')})"

        state_info = [
            f"Current Time: {self._get_timestamp()}",
            f"Current Directory: {self.current_directory}",
            f"System: {system} ({platform.release()})",
            f"Shell Environment: {shell_type}",
            f"Python Version: {sys.version.split()[0]}",
        ]
        return "\n".join(state_info)

    def _format_todo_list(self) -> str:
        """格式化待办事项列表"""
        if not self.config.enable_todo_list:
            return ""
        return ""
        
        

    def _get_system_hint(self) -> Optional[str]:
        """获取状态栏字符串"""
        if not any([self.config.enable_todo_list, self.config.enable_system_state]):
            return None

        hint_parts = []
        if self.config.enable_system_state:
            hint_parts.append("=== SYSTEM STATE ===")
            hint_parts.append(self._get_system_status())
            hint_parts.append("")
        if self.config.enable_todo_list:
            hint_parts.append("=== CURRENT TASKS ===")
            hint_parts.append(self._format_todo_list())
            hint_parts.append("")

        if hint_parts:
            return "\n".join(hint_parts)
        return None



    def run_task(self, task: str) -> str:
        """执行任务"""
        # 1. 添加用户消息
        self.conversation_history.append({"role": "user", "content": task})

        # 2. 状态栏信息
        message_to_send = self.conversation_history.copy()  # 要发送的消息（上下文）
        system_hint = self._get_system_hint()
        if system_hint:
            message_to_send.append({"role": "user", "content": system_hint})

        return self._get_system_hint() or ""