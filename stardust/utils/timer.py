import functools
import time
from typing import  Callable
from time import strftime

from stardust.config.chroma import rgb
from stardust.utils.applogging import AppLogger

log = AppLogger(debug=True)


def AppTimer(func: Callable):
    """Provide the performance time of async function"""

    @functools.wraps(func)
    async def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        function_name = func.__name__
        module_name = (func.__code__.co_filename).rsplit("/", maxsplit=1)[-1]
        tag = f"[{module_name}]"

        value = await func(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time
        function = f"{rgb(function_name, 'blue')}{rgb('()', 'yellow')}"
        print(
            f"{strftime('%H:%M:%S')} {rgb(tag, 'green')}: {function} completed in {elapsed_time:0.7f}s"
        )
        return value

    return wrapper_timer


def AppTimerSync(func: Callable):
    """Provide the performance time of async function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        function_name = func.__name__
        module_name = (func.__code__.co_filename).rsplit("/", maxsplit=1)[-1]
        tag = f"[{module_name}]"

        value = func(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time
        function = f"{rgb(function_name, 'blue')}{rgb('()', 'yellow')}"
        print(
            f"{strftime('%H:%M:%S')} {rgb(tag, 'green')}: {function} completed in {elapsed_time:0.7f}s"
        )
        return value

    return wrapper_timer
