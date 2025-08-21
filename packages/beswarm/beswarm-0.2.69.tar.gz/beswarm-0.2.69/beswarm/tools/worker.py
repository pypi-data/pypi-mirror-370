from datetime import datetime
from typing import List, Dict, Union

from ..core import mcp_manager, broker, task_manager, kgm
from ..agents.planact import BrokerWorker
from ..agents.chatgroup import ChatGroupWorker
from ..aient.aient.plugins import register_tool


@register_tool()
async def worker(goal: str, tools: List[Union[str, Dict]], work_dir: str, cache_messages: Union[bool, List[Dict]] = None):
    start_time = datetime.now()
    worker_instance = BrokerWorker(goal, tools, work_dir, cache_messages, broker, mcp_manager, task_manager, kgm)
    result = await worker_instance.run()
    end_time = datetime.now()
    print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总用时: {end_time - start_time}")
    return result

@register_tool()
async def worker_gen(goal: str, tools: List[Union[str, Dict]], work_dir: str, cache_messages: Union[bool, List[Dict]] = None):
    start_time = datetime.now()
    worker_instance = BrokerWorker(goal, tools, work_dir, cache_messages, broker, mcp_manager, task_manager, kgm)
    async for result in worker_instance.stream_run():
        yield result
    end_time = datetime.now()
    print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总用时: {end_time - start_time}")

@register_tool()
async def chatgroup(tools: List[Union[str, Dict]], work_dir: str, cache_messages: Union[bool, List[Dict]] = None):
    start_time = datetime.now()
    worker_instance = ChatGroupWorker(tools, work_dir, cache_messages, broker, mcp_manager, task_manager, kgm)
    result = await worker_instance.run()
    end_time = datetime.now()
    print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总用时: {end_time - start_time}")
    return result