# -*- coding: utf-8 -*-
# ReAct 循环:  思考 -> 执行 -> 观察 -> 循环(思考/执行/观察) 直到任务完成 再回答

import json
import re
from llm import chat
from tool_registry import get_tools_description, execute_tool
from memory.short_term import ShortTermMemory



REACT_SYSTEM_PROMPT_TEMPLATE = """你是一个能完成复杂任务的智能助手，可以反复使用工具直到任务完成。

{tools_description}

每次回复必须是 JSON，三种格式之一：

1. 需要使用工具（可以多次使用）：
{{"type": "tool_call", "tool": "工具名", "params": {{"参数名": "参数值"}}, "thought": "我为什么用这个工具"}}

2. 任务已完成：
{{"type": "final_answer", "content": "最终答案内容"}}

3. 需要向用户提问：
{{"type": "ask_user", "question": "你的问题"}}

规则：
- 最多使用工具 {max_steps} 次
- 收集到足够信息后，必须给出 final_answer
- 不要用相同参数重复调用同一个工具
- 只返回 JSON"""



def _safe_parse_json(s: str) -> dict:
    """从AI回复中安全解析 JSON 字符串"""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # 提取 {...} json 字符串
        match = re.search(r'({.*?})', s, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # 未提取到 JSON 字符串, 返回默认
        return {"type": "final_answer", "content": s}



class ReactAgent:
    """
    带对话记忆的 ReAct 循环智能体, 能够自动使用工具完成任务.
    同一个实例 跨多次 run() 调用时 共享记忆(多轮对话).
    """

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
        self._memory = ShortTermMemory(max_messages=30)
        self._memory.add("system", REACT_SYSTEM_PROMPT_TEMPLATE.format(
            tools_description=get_tools_description(),
            max_steps=self.max_steps
        ))

    def run(self, user_task: str) -> str:
        """运行 ReAct 循环完成任务, 返回最终答案"""
        self._memory.add("user", user_task)

        for step in range(1, self.max_steps + 1):
            print(f"\n{'_'*40}")
            print(f"[步骤 {step}/{self.max_steps}]")

            ai_response = chat(self._memory.to_api_format())
            print(f"[AI 思考]: {ai_response}")
            self._memory.add("assistant", ai_response)

            decision = _safe_parse_json(ai_response)
            resp_type = decision.get("type")

            # 任务已完成
            if resp_type == "final_answer":
                print(f"[任务完成, 共 {step} 步]")
                return decision.get("content", "(无内容)")
            
            # 使用工具
            if resp_type == "tool_call":
                tool_name = decision.get("tool", "")
                tool_params = decision.get("params", {})
                tool_thought = decision.get("thought", "")

                print(f"[工具调用]: {tool_name}({tool_params}) -> {tool_thought}")
                tool_result = execute_tool(tool_name, tool_params)

                # 打印工具调用结果, 前 100 字个字符
                print(f"[工具调用结果]: {tool_result[:100]}...")

                # 工具调用结果, 作为"观察" 存储到记忆中
                self._memory.add("user", f"工具 {tool_name} 返回结果: \n{tool_result}")
                continue

            # 向用户提问
            if resp_type == "ask_user":
                user_answer = input(f"\nAgent 问你: {decision.get("question", "")}\n你: ")
                self._memory.add("user", user_answer)
                continue

            # 未知类型, 结束
            return str(decision)
        
        # 达到步骤上限, 强制要求给出答案
        print(f"\n[已达步骤上限 {self.max_steps}, 要求给出最终答案]")
        self._memory.add("user", "你已用完所有步骤, 请立即基于已有信息给出最终答案.")
        final_response = chat(self._memory.to_api_format())
        final_answer = _safe_parse_json(final_response)
        self._memory.add("assistant", final_response)
        return final_answer.get("content", final_response)
    

    def clear_memory(self) -> None:
        """清除对话历史 (保留 system 消息)."""
        self._memory.clear_non_system()

    def memory_count(self) -> int:
        """返回对话历史中 非系统消息数量."""
        return self._memory.count()
