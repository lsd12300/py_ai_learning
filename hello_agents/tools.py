# -*- coding: utf-8 -*-
# 工具函数

import os
import serpapi


def web_search(query: str, max_results: int = 3) -> str:
    """使用搜索引擎搜索"""
    params = {
        "engine": "duckduckgo",  # 可换成 "bing", "google" 等
        "q": query,
        "m": max_results,
    }
    
    api_key=os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "错误: SERPAPI_API_KEY 未在 .env文件中配置"

    client = serpapi.Client(api_key=api_key, timeout=10)

    try:
        response = client.search(params)
        data_json = response.as_dict()
        data = data_json.get("organic_results", [])

        # 提取搜索结果
        results = []
        for item in data:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            results.append(f"标题: {title}")
            results.append(f"部分内容: {snippet}")

        if results:
            return "\n".join(results)
        else:
            return f"没有找到 {query} 相关结果"
    except Exception as e:
        return f"搜索出错: {e}"
    


from typing import Dict, Callable

class ToolExecutor:
    """工具执行器, 负责管理和执行工具"""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Callable]] = {}

    def registerTool(self, tool_name: str, tool_description: str, func: Callable):
        """注册工具"""
        if tool_name in self.tools:
            print(f"警告: 工具 {tool_name} 已存在, 将被覆盖")

        self.tools[tool_name] = {"func": func, "description": tool_description}
        print(f"工具 {tool_name} 已注册")

    def getTool(self, tool_name: str) -> Callable:
        """获取工具"""
        return self.tools.get(tool_name, {}).get("func")
    
    def getAvailableTools(self) -> list:
        """获取所有可用工具的格式化描述字符串"""
        return "\n".join([f"- {tool_name}: {info.get('description', '')}" for tool_name, info in self.tools.items()])


if __name__ == "__main__":

    executor = ToolExecutor()

    executor.registerTool("web_search", "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。", web_search)

    print(executor.getAvailableTools())