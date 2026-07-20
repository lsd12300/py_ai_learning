# -*- coding: utf-8 -*-
# 搜索工具

import requests
import serpapi


def web_search(query: str, max_results: int = 3) -> str:
    """使用搜索引擎搜索"""
    params = {
        "engine": "duckduckgo",  # 可换成 "bing", "google" 等
        "q": query,
        "m": max_results,
    }

    client = serpapi.Client(api_key="7b87067194ba59bf8d28c09402f08c9827e45bcd096a4e237057032e2f6c69fb", timeout=10)

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
    except requests.Timeout:
        return f"搜索超时, 请稍后重试或换个关键词"
    except Exception as e:
        return f"搜索出错: {e}"
