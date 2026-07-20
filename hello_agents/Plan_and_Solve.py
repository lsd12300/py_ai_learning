# -*- coding: utf-8 -*-
# Plan-and-Solve 模式 Agent


# 规划器提示模板
PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""


import ast
from hello_agents.hello_agents.core.llm import LLM


class Planner:
    """规划器, 负责根据问题生成行动计划"""

    def __init__(self, llm: LLM):
        self.llm = llm

    def plan(self, question: str) -> list:
        """根据问题生成行动计划"""
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]

        print("--- 正在生成计划 ---")
        response = self.llm.think(messages) or ""
        print(f"✅ 计划已生成:\n{response}")

        # 解析计划
        try:
            plan_str = response.split("```python")[1].split("```")[0].strip()
            # 使用 ast.literal_eval 安全的执行字符串, 将其转换为Python列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 计划解析出错: {e}")
            print(f"原始响应: {response}")
            return []
        except Exception as e:
            print(f"❌ 计划解析出错: {e}")
            return []




# 执行器提示模板
#   需要包含的关键信息: 原始问题、完整的计划、历史步骤和结果、当前步骤
EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""


class Executor:
    """执行器, 负责根据行动计划执行任务"""
    def __init__(self, llm: LLM):
        self.llm = llm

    def execute(self, question: str, plan: list[str]) -> str:
        """根据行动计划执行任务"""
        history = ""   # 存储历史步骤和结果
        final_answer = ""
        print("\n--- 正在执行计划 ---")

        for i, step in enumerate(plan, 1):
            print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")
            
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",
                current_step=step
            )
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.think(messages) or ""
            history += f"步骤{i}: {step}\n结果: {response}\n\n"
            final_answer = response
            print(f"✅ 步骤 {i}/{len(plan)} 执行结果:\n{response}")

        return final_answer



class PlanAndSolveAgent:
    """
    Plan-and-Solve 模式 Agent.
    作为一个协调者(Orchestrator), 负责协调规划器和执行器, 确保任务按计划执行.
    """
    def __init__(self, llm: LLM):
        self.llm = llm
        self.planner = Planner(llm)
        self.executor = Executor(llm)

    def run(self, question: str) -> str:
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        # 1. 生成计划
        plan = self.planner.plan(question)
        if not plan:
            print("\n--- 任务终止 ---\n无法生成有效的行动计划.")
            return
        
        # 2. 执行计划
        final_answer = self.executor.execute(question, plan)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return final_answer
    

if __name__ == "__main__":
    try:
        llm = LLM()
        agent = PlanAndSolveAgent(llm)
        question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
        result = agent.run(question)
        print(result)
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
