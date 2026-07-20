# -*- coding: utf-8 -*-

from config import load_config
from agent_loop import ReactAgent
from planner import make_plan, print_plan
from executor import execute_plan



BANNER = """
==================================================
    AI Agent 系统 v1.0
==================================================
命令:
  直接输入   ->  对话模式(有记忆, 自动使用工具)
  /plan 任务 ->  规划模式(先制定计划 再执行)
  /clear     ->  清除对话记忆, 开始新对话
  /quit      ->  退出
==================================================
"""



def main():
    """主函数"""
    load_config()
    print(BANNER)

    agent = ReactAgent(max_steps=5)

    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见.\n")
            break

        if not user_input:
            continue

        # 退出
        if user_input.lower() in ("quit", "exit", "/quit", "/exit"):
            print("再见...")
            break

        # 清除记忆
        if user_input.lower() == "/clear":
            agent.clear_memory()
            print("记忆已清除, 开启新对话.\n")
            continue
        
        # 规划模式(Plan-Execute)
        if user_input.lower().startswith("/plan "):
            goal = user_input[6:].strip()
            if not goal:
                print("用法: /plan 任务\n")
                continue

            print("\n正在制定计划...")
            plan = make_plan(goal)
            print_plan(plan)

            # 用户确认执行
            try:
                confirm = input("确认执行计划吗？(y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\n已取消.\n")
                continue

            if confirm == "y":
                result = execute_plan(plan)
                print(f"\m[Plan-Execute]: {result}\n")
            else:
                print("已取消.\n")

            continue


        # 普通对话(ReAct 模式)
        result = agent.run(user_input)
        print(f"[ReactAgent]: {result}\n")
        print(f"(对话记忆: {agent.memory_count()} 条)\n")


if __name__ == "__main__":
    main()
