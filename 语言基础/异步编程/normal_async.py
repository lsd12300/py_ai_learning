# -*- coding: utf-8 -*-
# 常规异步流程

import asyncio


# 模拟异步耗时操作
async def io_task(name, delay):
    print(f"任务 {name} 开始，耗时 {delay} 秒")
    await asyncio.sleep(delay)  # 挂起，模拟耗时操作
    print(f"任务 {name} 完成")
    return f"结果-{name}"


# 并发执行
async def main_concurrent():
    # 创建任务, 立即进入事件循环调度, 不阻塞当前协程
    task_a = asyncio.create_task(io_task("A", 2))
    task_b = asyncio.create_task(io_task("B", 3))
    task_c = asyncio.create_task(io_task("C", 1))

    # gather 等待所有任务完成, 并返回结果
    results = await asyncio.gather(task_a, task_b, task_c)
    print(results)


# 启动
asyncio.run(main_concurrent())