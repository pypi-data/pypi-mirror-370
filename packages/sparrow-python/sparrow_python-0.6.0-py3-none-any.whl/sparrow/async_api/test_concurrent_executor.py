"""
ConcurrentExecutor 测试脚本

简单的功能验证测试
"""

import asyncio
import time
import random
from sparrow.async_api.concurrent_executor import ConcurrentExecutor, TaskItem


async def simple_task(data, meta=None):
    """简单测试任务"""
    delay = random.uniform(0.1, 0.3)
    await asyncio.sleep(delay)
    return f"处理完成: {data}"


async def error_task(data, meta=None):
    """可能出错的任务"""
    await asyncio.sleep(0.1)
    if random.random() < 0.3:  # 30% 概率出错
        raise ValueError(f"任务 {data} 出错了")
    return f"成功: {data}"


def custom_error_handler(error, task_data, retry_count):
    """自定义错误处理"""
    print(f"错误处理器: {task_data} 发生错误 {error} (第{retry_count}次重试)")
    return retry_count < 2  # 最多重试2次


async def test_basic_execution():
    """测试基本执行功能"""
    print("=== 测试基本执行功能 ===")
    
    executor = ConcurrentExecutor(
        concurrency_limit=3,
        max_qps=5,
        retry_times=2
    )
    
    tasks_data = [f"任务_{i}" for i in range(10)]
    
    start_time = time.time()
    results, progress = await executor.execute_batch(
        async_func=simple_task,
        tasks_data=tasks_data,
        show_progress=True
    )
    end_time = time.time()
    
    print(f"\n执行完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"成功: {sum(1 for r in results if r.status == 'success')}")
    print(f"失败: {sum(1 for r in results if r.status == 'error')}")
    
    # 验证结果顺序
    assert len(results) == 10
    assert all(r.task_id == i for i, r in enumerate(results))
    print("✅ 基本执行测试通过")


async def test_priority_execution():
    """测试优先级执行"""
    print("\n=== 测试优先级执行 ===")
    
    executor = ConcurrentExecutor(concurrency_limit=2)
    
    priority_tasks = [
        TaskItem(priority=3, task_id=0, data="低优先级"),
        TaskItem(priority=1, task_id=1, data="高优先级"),
        TaskItem(priority=2, task_id=2, data="中优先级"),
        TaskItem(priority=1, task_id=3, data="高优先级2"),
    ]
    
    results, _ = await executor.execute_priority_batch(
        async_func=simple_task,
        priority_tasks=priority_tasks,
        show_progress=True
    )
    
    print(f"\n执行顺序（按完成时间）:")
    for result in results:
        task = next(t for t in priority_tasks if t.task_id == result.task_id)
        print(f"  任务ID {result.task_id}: 优先级 {task.priority} - {task.data}")
    
    print("✅ 优先级执行测试通过")


async def test_error_handling():
    """测试错误处理和重试"""
    print("\n=== 测试错误处理和重试 ===")
    
    executor = ConcurrentExecutor(
        concurrency_limit=2,
        retry_times=3,
        error_handler=custom_error_handler
    )
    
    tasks_data = [f"任务_{i}" for i in range(8)]
    
    results, _ = await executor.execute_batch(
        async_func=error_task,
        tasks_data=tasks_data,
        show_progress=True
    )
    
    success_count = sum(1 for r in results if r.status == 'success')
    error_count = sum(1 for r in results if r.status == 'error')
    
    print(f"\n错误处理结果:")
    print(f"成功: {success_count}")
    print(f"失败: {error_count}")
    
    # 显示重试信息
    for result in results:
        if result.status == 'error':
            print(f"  任务 {result.task_id} 失败，重试了 {result.retry_count} 次")
    
    print("✅ 错误处理测试通过")


async def test_streaming():
    """测试流式处理"""
    print("\n=== 测试流式处理 ===")
    
    executor = ConcurrentExecutor(concurrency_limit=3)
    tasks_data = [f"流式任务_{i}" for i in range(15)]
    
    processed_count = 0
    batch_count = 0
    
    async for batch_result in executor.aiter_execute_batch(
        async_func=simple_task,
        tasks_data=tasks_data,
        batch_size=4,
        show_progress=True
    ):
        batch_count += 1
        batch_size = len(batch_result.completed_tasks)
        processed_count += batch_size
        print(f"  批次 {batch_count}: 收到 {batch_size} 个结果，总计 {processed_count}")
    
    assert processed_count == 15
    print("✅ 流式处理测试通过")


async def test_sync_interface():
    """测试同步接口"""
    print("\n=== 测试同步接口 ===")
    
    executor = ConcurrentExecutor(concurrency_limit=2)
    tasks_data = [f"同步任务_{i}" for i in range(5)]
    
    # 使用同步接口
    results, _ = executor.execute_batch_sync(
        async_func=simple_task,
        tasks_data=tasks_data,
        show_progress=True
    )
    
    print(f"\n同步执行完成，处理了 {len(results)} 个任务")
    assert len(results) == 5
    assert all(r.status == 'success' for r in results)
    print("✅ 同步接口测试通过")


async def main():
    """运行所有测试"""
    print("🚀 开始测试 ConcurrentExecutor\n")
    
    try:
        await test_basic_execution()
        await test_priority_execution()
        await test_error_handling()
        await test_streaming()
        await test_sync_interface()
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 