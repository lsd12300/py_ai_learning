# -*- coding: utf-8 -*-
# 统一LLM接口

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from typing import Iterator, List, Dict, Optional
from llm_adapters import create_adapter
from llm_response import LLMResponse, StreamStats
from exceptions import LLMException, HelloAgentsException


# 自动查找 .env 文件并加载
load_dotenv()


class LLM:
    """
    统一LLM客户端

    设计理念:
    - 统一配置: 只需要环境变量 LLM_MODEL_ID、LLM_API_KEY、LLM_BASE_URL、LLM_TIMEOUT
    - 自动适配: 根据 base_url 自动选择合适适配器
    - 统计信息: 返回Token使用统计, 响应耗时的信息, 方便日志记录
    - Thinking Model: 自动识别并处理推理过程
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
    ):
        """
        初始化LLM客户端

        参数优先级: 传入参数 > 环境变量

        :param model: 模型ID.  LLM_MODEL_ID
        :param api_key: API密匙.  LLM_API_KEY
        :param base_url: 服务地址.  LLM_BASE_URL
        :param temperature: 温度参数, 控制模型的随机性.  默认0.7
        :param max_tokens: 最大生成token数
        :param timeout: 请求超时时间, 单位秒. LLM_TIMEOUT.  默认60秒
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

        # 验证必要参数
        if not self.model:
            raise HelloAgentsException("必须提供模型名称（model参数或LLM_MODEL_ID环境变量）")
        if not self.api_key:
            raise HelloAgentsException("必须提供API密匙（api_key参数或LLM_API_KEY环境变量）")
        if not self.base_url:
            raise HelloAgentsException("必须提供服务地址（base_url参数或LLM_BASE_URL环境变量）")
        
        # 创建OpenAI客户端
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )


    def think(self, messages: List[Dict[str, str]], temperature: Optional[float] = None) -> Iterator[str]:
        """
        调用大语言模型进行思考，并返回流式响应。
        这是主要的调用方法，默认使用流式响应以获得更好的用户体验。

        Args:
            messages: 消息列表
            temperature: 温度参数，如果未提供则使用初始化时的值

        Yields:
            str: 流式响应的文本片段
        """
        print(f"正在调用 {self.model} 模型...")
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens,
            )

            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                if content:
                    print(content, end="", flush=True)
                    yield content
            print("") # 流式输出结束后, 换行

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise HelloAgentsException(f"调用LLM错误: {str(e)}")
        
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        非流式调用LLM，返回完整响应。
        适用于不需要流式输出的场景。
        """
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            raise HelloAgentsException(f"调用LLM错误: {str(e)}")
        
    def stream_invoke(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """
        流式调用LLM的别名方法，与think方法功能相同。
        保持向后兼容性。
        """
        temperature=kwargs.get("temperature")
        return self.think(messages, temperature)
        
