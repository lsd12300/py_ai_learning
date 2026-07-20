# -*- coding: utf-8 -*-
# Plan-Execute 模式  中的执行器


import json
import re
from llm import chat
from tool_registry import execute_tool


def _infer_params(tool_name: str, step_desc: str, goal: str) -> dict:
    """根据步骤推断工具参数"""
    prompt = f"""任务总目标: {goal}
当前步骤: {step_desc}
需要调用工具: {tool_name}

请生成调用工具所需的参数, 只返回JSON对象.
注意: 当字符串内部有双引号时, 需要转义为 \\"
例如 调用web_search时: {{\"query\": \"搜索关键词\"}}
"""
    response = chat([{"role": "user", "content": prompt}])
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # 提取 {...} json 字符串
        match = re.search(r'({.*?})', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        
    return {}


def execute_plan(plan: dict) -> dict:
    """按计划逐步执行, 最终汇总成完整答案."""
    goal = plan.get('goal', '未知')
    steps = plan.get('steps', [])

    print(f"\n开始执行计划: {goal}")
    results: list[str] = []

    for step in steps:
        step_num = step.get('step', -1)
        step_desc = step.get('description', '')
        tool_name = step.get('tool', None)
        
        print(f"\n{'_'*40}")
        print(f"步骤 {step_num}: {step_desc}")

        if tool_name:
            params = _infer_params(tool_name, step_desc, goal)
            print(f"[调用工具 {tool_name}], 参数: {params}")
            result = execute_tool(tool_name, params)
            print(f"[工具调用结果]: {result[:200]}...")
        else:
            # 不需要工具, 让 AI 直接处理
            result = chat([{"role": "user", "content": f"请完成这个步骤: {step_desc}\n (这是任务 {goal} 的一个步骤)"}])
            print(f"[AI 完成]: {result[:200]}...")
        
        results.append(f"步骤{step_num} ({step_desc}): \n{result}")

    # 整合所有步骤结果
    print(f"\n{'_'*40}")
    print(f"[整合结果, 生成最终答案...]")

    summary_prompt = f"""你完成了任务: {goal}

以下是每个步骤的执行结果:
{'='*20}
{chr(10).join(results)}
{'='*20}

请基于以上信息, 给出完整、清晰、结构化的最终答案.
"""
    summary = chat([{"role": "user", "content": summary_prompt}])
    return summary

