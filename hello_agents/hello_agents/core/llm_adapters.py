# -*- coding: utf-8 -*-
# LLM适配器.  兼容不同LLM服务的接口


import asyncio
import time
import json
from abc import ABC, abstractmethod
from typing import Optional, Iterator, List, Dict, Any, Union, AsyncIterator

from .llm_response import LLMResponse, StreamStats, LLMToolResponse, ToolCall
from .exceptions import HelloAgentsException


class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, api_key: str, base_url: Optional[str], timeout: int, model: str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = None
        self._async_client = None

    @abstractmethod
    def create_client(self):
        """创建LLM客户端"""
        pass

    def create_async_client(self):
        """创建异步LLM客户端"""
        return None
    
    @abstractmethod
    def invoke(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """非流式调用"""
        pass

    @abstractmethod
    def stream_invoke(self, messages: List[Dict], **kwargs) -> Iterator[str]:
        """流式调用"""
        pass

    async def astream_invoke(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """
        异步流式调用

        默认实现: 队列 + 线程池包装的同步流式方法
        """
        # asyncio.Queue队列是线程不安全的, 只能在事件循环中使用
        #   必须配合 asyncio.run_coroutine_threadsafe 来在异步线程中运行
        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        # 普通的同步函数
        def _stream_to_queue():
            try:
                for chunk in self.stream_invoke(messages, **kwargs):
                    # queue.put(chunk) 是一个异步协程, 作用是将 chunk 放入队列, 如果队列已满, 则等待队列有空间
                    # asyncio.run_coroutine_threadsafe 是线程安全的函数, 允许另一个线程向目标事件循环提交异步协程
                    #    这行代码的作用是将 chunk 通过队列从同步线程传递到了异步事件循环中
                    asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(queue.put(e), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        # 将同步函数 _stream_to_queue 提交到默认的线程池执行器中运行
        loop.run_in_executor(None, _stream_to_queue)

        # 从队列中获取数据
        while True:
            # 阻塞等待 从队列中获取数据
            chunk = await queue.get()
            if chunk is None:
                break
            if isinstance(chunk, Exception):
                raise chunk
            yield chunk


    @abstractmethod
    def invoke_with_tools(self, messages: List[Dict], tools: List[Dict],  **kwargs) -> LLMToolResponse:
        """工具调用"""
        pass

    def _is_thinking_model(self, model_name: str) -> bool:
        """判断模型是否为推理模型"""
        thinking_keywords = ["reasoner", "o1", "o3", "thinking"]
        model_lower = model_name.lower()
        return any(keyword in model_lower for keyword in thinking_keywords)



class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI LLM适配器"""

    def create_client(self):
        """创建OpenAI客户端"""
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )
    
    def create_async_client(self):
        """创建异步OpenAI客户端"""
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )
    
    def invoke(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """非流式调用"""
        if not self._client:
            self._client = self.create_client()
        
        start_time = time.time()

        try:
            response = self._client.chat.completions.create(    
                model=self.model,
                messages=messages,
                **kwargs
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # 提取内容
            choice = response.choices[0]
            content = choice.message.content or ""
            reasoning_content = None

            # Thinking Model 处理
            if self._is_thinking_model(self.model):
                # OpenAI o1系列: reasoning_content 在 message中
                if hasattr(choice.message, "reasoning_content"):
                    reasoning_content = choice.message.reasoning_content
                # DeepSeek reasoner: 可能在其他字段
                elif hasattr(choice, "reasoning_content"):
                    reasoning_content = choice.reasoning_content

            # 提取 token用量
            usage = {}
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "total_tokens": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }

            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage,
                latency_ms=latency_ms,
                reasoning_content=reasoning_content,
            )

        except Exception as e:
            raise HelloAgentsException(f"OpenAI API 调用失败: {str(e)}")
        
    def stream_invoke(self, messages: List[Dict], **kwargs) -> Iterator[str]:
        """流式调用"""
        if not self._client:
            self._client = self.create_client()

        start_time = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )

            collected_content = []
            reasoning_content = None
            usage = {}

            for chunk in response:
                choices = getattr(chunk, "choices", None)
                if choices:
                    delta = getattr(choices[0], "delta", None)
                    if delta is not None:
                        # 提取内容
                        content = getattr(delta, "content", None)
                        if content:
                            collected_content.append(content)
                            yield content

                        # Thinking Model 处理
                        if self._is_thinking_model(self.model):
                            reasoning_delta = getattr(delta, "reasoning_content", None)
                            if reasoning_delta:
                                if reasoning_content is None:
                                    reasoning_content = ""
                                reasoning_content += reasoning_delta

                # 提取 token用量（流式最后一个chunk可能包含）
                if hasattr(chunk, "usage") and chunk.usage:
                    usage = {
                        "total_tokens": chunk.usage.total_tokens,
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                    }

            latency_ms = int((time.time() - start_time) * 1000)

            self.last_stats = StreamStats(
                model=self.model,
                latency_ms=latency_ms,
                usage=usage,
                reasoning_content=reasoning_content,
            )

        except Exception as e:
            raise HelloAgentsException(f"OpenAI API 流式调用失败: {str(e)}")
        
    async def astream_invoke(self, messages: List[Dict], **kwargs) -> AsyncIterator[str]:
        """真正的异步流式调用"""
        if not self._async_client:
            self._async_client = self.create_async_client()

        start_time = time.time()

        try:
            response = await self._async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )

            collected_content = []
            reasoning_content = None
            usage = {}

            async for chunk in response:
                choices = getattr(chunk, "choices", None)
                if choices:
                    delta = getattr(choices[0], "delta", None)
                    if delta is not None:
                        # 提取内容
                        content = getattr(delta, "content", None)
                        if content:
                            collected_content.append(content)
                            yield content

                        # Thinking Model 处理
                        if self._is_thinking_model(self.model):
                            reasoning_delta = getattr(delta, "reasoning_content", None)
                            if reasoning_delta:
                                if reasoning_content is None:
                                    reasoning_content = ""
                                reasoning_content += reasoning_delta

                # 提取 token用量（流式最后一个chunk可能包含）
                if hasattr(chunk, "usage") and chunk.usage:
                    usage = {
                        "total_tokens": chunk.usage.total_tokens,
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                    }

            latency_ms = int((time.time() - start_time) * 1000)

            self.last_stats = StreamStats(
                model=self.model,
                latency_ms=latency_ms,
                usage=usage,
                reasoning_content=reasoning_content,
            )
        
        except Exception as e:
            raise HelloAgentsException(f"OpenAI API 异步流式调用失败: {str(e)}")
        
    
    def invoke_with_tools(self, messages: List[Dict], tools: List[Dict], tool_choice: Union[str, Dict], **kwargs) -> LLMToolResponse:
        """工具调用"""
        if not self._client:
            self._client = self.create_client()

        start_time = time.time()
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs
            )

            latency_ms = int((time.time() - start_time) * 1000)
            message = response.choices[0].message

            tool_calls = []
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_calls.append(ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    ))

            usage = {}
            if response.usage:
                usage = {
                    "total_tokens": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            
            return LLMToolResponse(
                content=message.content,
                tool_calls=tool_calls,
                model=response.model,
                usage=usage,
                latency_ms=latency_ms,
            )

        except Exception as e:
            raise HelloAgentsException(f"OpenAI 工具调用失败: {str(e)}")
    



def create_adapter(
    api_key: str,
    base_url: Optional[str],
    timeout: int,
    model: str,
) -> BaseLLMAdapter:
    """
    根据 base_url 创建LLM适配器

    逻辑:
    - anthropic.com -> AnthropicAdapter
    - googleapis.com 或 generativelanguage -> GeminiAdapter
    - 其他 -> OpenAIAdapter
    """
    if base_url:
        url_lower = base_url.lower()
        if "anthropic.com" in url_lower:
            pass
        elif "googleapis.com" in url_lower or "generativelanguage" in url_lower:
            pass

    return OpenAIAdapter(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        model=model,
    )