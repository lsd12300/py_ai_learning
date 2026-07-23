# -*- coding: utf-8 -*-
# 生产者-消费者模型
#  1. 传统多线程方案 (queue.Queue + ThreadPoolExecutor)
#      线程级并发
#  2. 异步协程方案 (asyncio.Queue + loop.run_in_executor)
#      协程级并发, 不阻塞线程


import asyncio
import time
import random
import concurrent.futures


# 模拟同步阻塞 IO任务 (需放在线程池执行)
def sync_blocking_work(item):
    sleep_time = random.uniform(0.1, 0.4) # 随机耗时 0.1-0.4 秒
    time.sleep(sleep_time)  # 阻塞操作
    return f"处理 {item} 耗时 {sleep_time:.2f} 秒"


async def async_producer(queue, total):
    """异步生产者"""
    for i in range(total):
        await asyncio.sleep(0.05)  # 模拟异步生产间隔
        await queue.put(f"Task-{i}")
        print(f"[生产者] 生产 Task-{i}")

    # 发送完成信号 (或叫 哨兵).  数量等于 max_workers
    for _ in range(5):
        await queue.put(None)
    print("[生产者] 生产完毕, 发送完成信号")


async def async_consumer(queue, executor):
    """异步消费者: 从队列取任务, 把阻塞操作扔给线程池执行"""
    loop = asyncio.get_running_loop()
    while True:
        item = await queue.get()
        if item is None:  # 哨兵信号
            queue.task_done()
            print("[消费者] 收到完成信号, 即将关闭")
            break

        # 关键: 将同步阻塞函数提交到线程池执行, 不阻塞事件循环
        result = await loop.run_in_executor(executor, sync_blocking_work, item)
        print(f"[消费者] 处理 {item} 结果: {result}")
        queue.task_done()


async def main():
    # 创建异步队列
    queue = asyncio.Queue(maxsize=10)

    # 创建线程池(消费者数量)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 启动生产者协程
        producer_task = asyncio.create_task(async_producer(queue, 30))

        # 启动多个消费者协程
        consumer_tasks = [asyncio.create_task(async_consumer(queue, executor)) for _ in range(5)]

        # 等待生产者完成
        await producer_task

        # 等待队列清空 (所有 task_done 被调用)
        await queue.join()
        print("队列已清空, 等待消费者完成...")

        # 等待所有消费者完成
        await asyncio.gather(*consumer_tasks)
    
    print("[全部完成]")


if __name__ == "__main__":
    asyncio.run(main())