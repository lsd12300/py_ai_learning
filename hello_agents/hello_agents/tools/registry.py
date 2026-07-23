# -*- coding: utf-8 -*-
# 工具注册器


from typing import Optional, Any, Callable, Dict, List
from base import Tool


class ToolRegistry:
    """
    HelloAgents工具注册表

    提供工具的注册、管理和执行功能。
    支持两种工具注册方式：
    1. Tool对象注册（推荐）
    2. 函数直接注册（简便）
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._functions: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """注册Tool对象"""
        if tool.name in self._tools:
            print(f"⚠️ 警告:工具 '{tool.name}' 已存在，将被覆盖。")
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")

    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """
        直接注册函数作为工具（简便方式）

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"⚠️ 警告:工具 '{name}' 已存在，将被覆盖。")
        self._functions[name] = {"func": func, "description": description}
        print(f"✅ 工具 '{name}' 已注册。")

    def unregister(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            print(f"✅ 工具 '{name}' 已注销。")
        elif name in self._functions:
            del self._functions[name]
            print(f"✅ 工具 '{name}' 已注销。")
        else:
            print(f"⚠️ 警告:工具 '{name}' 不存在。")

    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具对象"""
        return self._tools.get(name)

    def get_function(self, name: str) -> Optional[Callable]:
        """获取函数工具"""
        return self._functions.get(name, {}).get("func")
    
    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            input_text: 输入参数

        Returns:
            工具执行结果
        """
        if name in self._tools:
            tool = self._tools[name]
            try:
                # 简化参数传递，直接传入字符串
                return tool.run({"input": input_text})
            except Exception as e:
                return f"❌ 执行工具 '{tool.name}' 失败: {str(e)}"
        elif name in self._functions:
            func = self._functions[name]["func"]
            try:
                return func(input_text)
            except Exception as e:
                return f"❌ 执行函数 '{name}' 失败: {str(e)}"
        else:
            return f"❌ 工具 '{name}' 不存在。"



    def get_tools_descriptions(self) -> str:
        """获取所有可用工具的格式化字符串描述"""
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具."
    
