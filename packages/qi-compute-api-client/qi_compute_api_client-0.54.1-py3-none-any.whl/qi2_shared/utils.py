import asyncio
import concurrent
from typing import Any, Coroutine


def run_async(async_function: Coroutine[Any, Any, Any]) -> Any:
    try:
        _ = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(async_function)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(asyncio.run, async_function).result()
