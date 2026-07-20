# -*- coding: utf-8 -*-
# 反思循环


from typing import Dict, List, Optional, Any

class Memory:
    """简单的短期记忆模块, 用于存储智能体的行动与反思轨迹."""
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        """
        添加一条记录到记忆中.
        
        参数:
        - record_type (str): 记录类型, 如 "execution" 或 "reflection".
        - content (str): 记录的具体内容.
        """
        record = {"type": record_type, "content": content}
        self.records.append(record)
        print(f" 记忆更新, 新增一条 {record_type} 记录.")

    def get_trajectory(self) -> str:
        """
        将所有记忆格式化为一个连贯的字符串文本, 用于构建提示词.
        """
        trajectory_parts = []
        for record in self.records:
            if record["type"] == "execution":
                trajectory_parts.append(f"--- 上一轮尝试 ---\n{record['content']}")
            elif record["type"] == "reflection":
                trajectory_parts.append(f"--- 评审员反馈 ---\n{record['content']}")

        return "\n\n".join(trajectory_parts)
    
    def get_last_execution(self) -> Optional[str]:
        """
        获取最近一次的执行结果.
        如果不存在, 则返回 None.
        """
        for record in self.records:
            if record["type"] == "execution":
                return record["content"]
        return None



# 初始执行提示词
INITIAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求，编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。

要求: {task}

请直接输出代码，不要包含任何额外的解释。
"""


# 反思提示词
REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法工程师，对代码的性能有极致的要求。
你的任务是审查以下Python代码，并专注于找出其在**算法效率**上的主要瓶颈。

# 原始任务:
{task}

# 待审查的代码:
```python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种**算法上更优**的解决方案来显著提升性能。
如果存在，请清晰地指出当前算法的不足，并提出具体的、可行的改进算法建议（例如，使用筛法替代试除法）。
如果代码在算法层面已经达到最优，才能回答“无需改进”。

请直接输出你的反馈，不要包含任何额外的解释。
"""


# 优化提示词
REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务:
{task}

# 你上一轮尝试的代码:
{last_code_attempt}

# 评审员的反馈:
{feedback}

请根据评审员的反馈，生成一个优化后的新版本代码。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8编码规范。
请直接输出优化后的代码，不要包含任何额外的解释。
"""



from hello_agents.hello_agents.core.llm import LLM

class ReflectionAgent:
    """反思智能体, 负责协调智能体的反思与优化过程."""
    def __init__(self, llm: LLM, max_iterations: int = 3):
        self.llm = llm
        self.memory = Memory()
        self.max_iterations = max_iterations

    def run(self, task: str) -> str:
        print(f"\n--- 开始执行任务 ---\n任务: {task}")

        # 1. 初始执行
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)

        # 2. 迭代循环: 反思与优化
        for iteration in range(self.max_iterations):
            print(f"\n--- 第 {iteration+1}/{self.max_iterations} 轮迭代 ---")

            # 反思
            print(f"\n-> 正在反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # 检测停止
            if "无需改进" in feedback:
                print("\n✅ 反思认为代码已无需改进，任务完成。")
                break
            
            # 优化
            print("\n-> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(task=task, last_code_attempt=last_code, feedback=feedback)
            optimized_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", optimized_code)

        final_code = self.memory.get_last_execution()
        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_code}\n```")
        return final_code


    def _get_llm_response(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.llm.think(messages) or ""
        return response



if __name__ == "__main__":
    llm = LLM()
    agent = ReflectionAgent(llm, max_iterations=3)
    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    agent.run(task)