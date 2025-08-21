# -*- coding: utf-8 -*-
# @Author  : zhousf-a
# @Date    : 2024/3/25 
# @Function:
import time
import functools
from asyncio.coroutines import iscoroutinefunction


def time_cost(logger=None):

    def decorator(func):
        @functools.wraps(func)
        def fun(*args, **kwargs):
            t = time.perf_counter()
            result = func(*args, **kwargs)
            if logger:
                logger.debug(f'func {func.__name__} time cost:{time.perf_counter() - t:.8f}s')
            else:
                print(f'func {func.__name__} time cost:{time.perf_counter() - t:.8f}s')
            return result

        async def func_async(*args, **kwargs):
            t = time.perf_counter()
            result = await func(*args, **kwargs)
            if logger:
                logger.debug(f'func {func.__name__} time cost:{time.perf_counter() - t:.8f}s')
            else:
                print(f'func {func.__name__} time cost:{time.perf_counter() - t:.8f}s')
            return result

        if iscoroutinefunction(func):
            return func_async
        else:
            return fun
    return decorator
