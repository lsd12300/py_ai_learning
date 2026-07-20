# -*- coding: utf-8 -*-
# Plan-Execute 模式  中的计划器

import json
import re
from llm import chat


PLANNER_PROMPT_TEMPLATE = """你是一个任务规划专家。

用户给你一个复杂任务，把它分解成 3-6 个清晰、可执行的步骤。

可用工具：web_search（搜索）、get_weather（天气）、calculate（计算）、get_current_time（时间）

要求：
- 每步要具体，能直接执行
- 需要工具的步骤标明工具名，不需要的填 null
- 步骤数控制在 3-6 步，不要过多

只返回 JSON，不要加任何其他文字：
注意: 当字符串内部有双引号时, 需要转义为 \\"
{
  "goal": "任务总目标一句话描述",
  "steps": [
    {"step": 1, "description": "具体步骤描述", "tool": "工具名或null"},
    {"step": 2, "description": "具体步骤描述", "tool": "工具名或null"}
  ]
}"""


def make_plan(user_task: str) -> dict:
    """根据用户任务, 生成任务计划"""
    response = chat([
        { "role": "system", "content": PLANNER_PROMPT_TEMPLATE},
        { "role": "user", "content": f"请为这个任务制定自行计划: {user_task}"}
    ])

    try:
        print(response)
        return json.loads(response)
    except json.JSONDecodeError:
        # 提取 {...} json 字符串
        match = re.search(r'({.*?})', response, re.DOTALL)
        if match:
            print(match.group(1))
            return json.loads(match.group(1))
        
    # 解析失败, 包装成单步计划
    return {"goal": user_task, "steps": [{"step": 1, "description": user_task, "tool": None}]}


def print_plan(plan: dict):
    """打印任务计划"""
    print(f"\n目标: {plan.get('goal', '未知')}")
    steps = plan.get('steps', [])
    print(f"步骤数: {len(steps)}")
    for step in steps:
        tool_hint = f"    (工具: {step['tool']})" if step.get('tool') else ""
        print(f"    步骤 {step.get('step', -1)}: {step.get('description', '无描述')}{tool_hint}")
