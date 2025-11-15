import asyncio
from functools import wraps
from typing import Callable, Any


def run_in_executor(func: Callable) -> Callable:
    """Декоратор для запуска блокирующих функций в отдельном потоке"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper