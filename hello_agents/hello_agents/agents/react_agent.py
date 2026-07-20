# -*- coding: utf-8 -*-
# ReAct 模式 Agent
#   不断循环三个步骤
#     1. Thought (思考)
#     2. Action (行动)
#     3. Observation (观察)


# ReAct 提示词模版
#   定义了 Agent 和 LLM之间交互的规范:
#     - 角色定义. 设定 LLM的角色
#     - 工具清单.
#     - 格式约定. 最重要的部分, 强制 LLM 的输出具有结构性, 方便后续解析和使用。
#     - 动态上下文. 将用户的原始问题和不断累积的交互历史注入, 让 LLM 基于完整的上下文进行决策。
REACT_PROMPT_TEMPLATE = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

Thought: 分析问题，确定需要什么信息，制定研究策略。
Action: 选择合适的工具获取信息，格式为：
- `{{tool_name}}[{{tool_input}}]`：调用工具获取信息。
- `Finish[研究结论]`：当你有足够信息得出结论时。

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""


import re
from typing import Optional
from hello_agents.hello_agents.tools.registry import ToolRegistry
from hello_agents.tools import ToolExecutor
from hello_agents.hello_agents.core.llm import LLM

class ReActAgent:
    """ReAct 模式智能体"""
    def __init__(self, llm: LLM, tool_registry: Optional[ToolRegistry] = None):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str) -> str:
        """运行 ReAct 模式智能体 回答问题"""
        self.history = []   # 每次运行重置历史记录
        current_step = 0

        # 最大步数 防止无限循环
        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tools.getAvailableTools()
            history_desc = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_desc
            )

            # 2. 调用 LLM 思考
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.think(messages=messages)

            if not response:
                print("错误: LLM 未返回有效响应")
                break


            # 3. 解析 LLM 输出
            thought, action = self._parse_output(response)
            if thought:
                print(f"思考: {thought}")

            if not action:
                print("警告: 未能解析出有效的 Action 字段, 流程中断")
                break
            
            # 4. 执行 Action
            if action.startswith("Finish"):
                # 提取最终答案
                final_answer = re.search(r"Finish\[(.*)\]", action, re.DOTALL).group(1).strip()
                print(f"🎉 最终答案: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append(f"Observation: 无效的Action格式, 请检查.")
                continue
            
            print(f" 行动: {tool_name}[{tool_input}]")
            tool_func = self.tools.getTool(tool_name)
            observation = tool_func(tool_input) if tool_func else f"错误: 未找到名为 {tool_name} 的工具."
            
            print(f"👀 观察: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")
        
        print("已达到最大步数, 流程终止.")
        return None
    
    
    def _parse_output(self, output: str) -> str:
        """解析 LLM 输出, 提取Thought和Action"""
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", output, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", output, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action
    
    def _parse_action(self, action: str) -> str:
        """解析 Action 字段, 提取工具名称和输入"""
        match = re.search(r"(\w+)\[(.*)\]", action, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None


if __name__ == "__main__":
    from hello_agents.tools import web_search
    llm = LLM()
    tools = ToolExecutor()
    tools.registerTool("web_search", "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。", web_search)
    agent = ReActAgent(llm, tools)
    question = "华为最新的手机是哪一款? 它的主要卖点是什么?"
    answer = agent.run(question)
    print(answer)