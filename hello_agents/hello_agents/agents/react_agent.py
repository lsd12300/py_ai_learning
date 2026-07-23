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
from typing import Optional, List, Tuple
from ..core.agent import Agent
from ..core.llm import LLM
from ..core.config import Config
from ..core.message import Message
from ..tools.registry import ToolRegistry



class ReActAgent(Agent):
    """
    ReAct (Reasoning and Acting) Agent
    
    结合推理和行动的智能体，能够：
    1. 分析问题并制定行动计划
    2. 调用外部工具获取信息
    3. 基于观察结果进行推理
    4. 迭代执行直到得出最终答案
    
    这是一个经典的Agent范式，特别适合需要外部信息的任务。
    """
    def __init__(
            self,
            name: str,
            llm: LLM,
            tool_registry: Optional[ToolRegistry] = None,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            max_steps: int = 5,
            custom_prompt: Optional[str] = None
    ):
        """
        初始化ReActAgent

        Args:
            name: Agent名称
            llm: LLM实例
            tool_registry: 工具注册表（可选，如果不提供则创建空的工具注册表）
            system_prompt: 系统提示词
            config: 配置对象
            max_steps: 最大执行步数
            custom_prompt: 自定义提示词模板
        """
        super().__init__(name, llm, system_prompt, config)
        if tool_registry is None:
            self.tool_registry = ToolRegistry()
        else:
            self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history: List[str] = []

        # 设置提示词模版: 用户自定义优先, 否则使用默认模板
        self.prompt_template = custom_prompt if custom_prompt else REACT_PROMPT_TEMPLATE


    def add_tool(self, tool):
        """
        添加工具到工具注册表
        支持MCP工具的自动展开

        Args:
            tool: 工具实例(可以是普通Tool或MCPTool)
        """
        # 检查是否为MCP工具
        if hasattr(tool, "auto_expand") and tool.auto_expand:
            # MCP 工具自动展开为多个工具
            if hasattr(tool, "_available_tools") and tool._available_tools:
                for mcp_tool in tool._available_tools:
                    pass
                    # from ..tools.base import Tool
                    # wrapped_tool = Tool(
                    #     name=f"{tool.name}_{mcp_tool.name}",
                    #     description=mcp_tool.get("description", ""),
                    #     func=lambda input_text, t=tool: tn=mcp_tool['name']: t.run({
                    #         "action": "call_tool",
                    #         "tool_name": tn,
                    #         "arguments": {"input": input_text}
                    #     })
                    # )
            else:
                self.tool_registry.add_tool(tool)
        else:
            self.tool_registry.add_tool(tool)


    def run(self, input_text: str) -> str:
        """
        运行ReAct Agent
        
        Args:
            input_text: 用户问题
            **kwargs: 其他参数
            
        Returns:
            最终答案
        """
        self.current_history = []   # 每次运行重置历史记录
        current_step = 0
        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")

        # 最大步数 防止无限循环
        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_registry.get_tools_descriptions()
            history_desc = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_desc
            )

            # 2. 调用 LLM 思考
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.invoke(messages=messages)

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
                final_answer = self._parse_action_input(action)
                print(f"🎉 最终答案: {final_answer}")

                # 保存到历史记录
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.current_history.append(f"Observation: 无效的Action格式, 请检查.")
                continue
            
            print(f" 行动: {tool_name}[{tool_input}]")
            observation = self.tool_registry.execute_tool(tool_name, tool_input)
            print(f"👀 观察: {observation}")

            self.current_history.append(f"Action: {action}")
            self.current_history.append(f"Observation: {observation}")
        
        print("已达到最大步数, 流程终止.")
        final_answer = "抱歉，我无法在限定步数内完成这个任务。"
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        
        return final_answer
    
    
    def _parse_output(self, output: str) -> Tuple[Optional[str], Optional[str]]:
        """解析 LLM 输出, 提取Thought和Action"""
        # Thought: 匹配到 Action: 或文本末尾
        # thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", output, re.DOTALL)
        thought_match = re.search(r"Thought: (.*)", output)
        # Action: 匹配到文本末尾
        # action_match = re.search(r"Action:\s*(.*?)$", output, re.DOTALL)
        action_match = re.search(r"Action: (.*)", output)
        
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action
    
    def _parse_action(self, action_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析行动文本，提取工具名称和输入"""
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def _parse_action_input(self, action_text: str) -> str:
        """解析行动输入"""
        match = re.match(r"\w+\[(.*)\]", action_text)
        return match.group(1) if match else ""