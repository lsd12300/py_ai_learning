# -*- coding: utf-8 -*-
# 调用 llm

import os
from openai import OpenAI

_client: OpenAI | None = None  # 单例模式

def get_client() -> OpenAI:
    """获取 OpenAI 客户端实例"""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
    return _client


def chat(message: list[dict]) -> str:
    req = get_client().chat.completions.create(
        model=os.environ.get("OPENAI_MODEL"),
        messages=message,
        temperature=0,  # 温度, 控制输出的随机性, 0 表示确定性输出
    )
    return req.choices[0].message.content