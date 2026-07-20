# -*- coding: utf-8 -*-
# 工具注册

from tools.search import web_search
from tools.weather import get_weather
from tools.datetime_tool import get_current_time
from tools.calculator import calculate



# 工具描述
TOOLS : dict[str, dict] = {
    "web_search": {
        "description": "搜索互联网上的信息. 适合查找新闻、事件、最新资讯",
        "function": web_search,
        "parameters": {
            "query": "要搜索的关键词, 字符串类型.  例如: 'Python 3 新特性'",
        },
    },
    "get_weather": {
        "description": "查询指定城市的天气信息",
        "function": get_weather,
        "parameters": {
            "city": "城市名称, 字符串类型.  例如: '北京'",
        },
    },
    "get_current_time": {
        "description": "获取当前时间, 默认北京时间",
        "function": get_current_time,
        "parameters": {
            "timezone": "时区名称, 字符串类型.  例如: 'Asia/Shanghai'",
        },
    },
    "calculate": {
        "description": "计算数学表达式, 支持加减乘除和括号. 只用于数学计算, 不用于其他问题",
        "function": calculate,
        "parameters": {
            "expression": "数学表达式, 字符串类型.  例如: '2 + 3 * 4'",
        },
    },
}


def get_tools_description() -> str:
    """生成给AI看的工具描述字符串"""
    lines = ["你有以下工具可以使用:\n"]
    for tool_name, tool in TOOLS.items():
        lines.append(f"工具名: {tool_name}")
        lines.append(f"用途: {tool['description']}")
        lines.append(f"参数: {tool.get('parameters', '无')}")
        lines.append("")
    return "\n".join(lines)


def execute_tool(tool_name: str, arguments: dict) -> str:
    """执行指定工具, 返回执行结果字符串"""
    if tool_name not in TOOLS:
        return f"没有工具 {tool_name}, 可用的工具有: {list(TOOLS.keys())}"
    
    tool_func = TOOLS[tool_name]["function"]
    try:
        return str(tool_func(**arguments))
    except TypeError as e:
        return f"工具 {tool_name} 参数错误: {e}"
    except Exception as e:
        return f"工具 {tool_name} 执行出错: {e}"
