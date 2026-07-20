# -*- coding: utf-8 -*-
# 工具行为


def get_weather(city: str) -> str:
    """获取城市的天气"""
    mock_data = {
        "北京": "晴，15°C，东风3级",
        "上海": "多云，18°C，南风2级",
        "广州": "小雨，22°C，偏东风",
    }
    return mock_data.get(city, f"{city} 的天气是未知的")
