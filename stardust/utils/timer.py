import functools
import time
from typing import Callable

from stardust.config.chroma import rgb
from stardust.utils.applogging import HelioLogger

log = HelioLogger(debug=True)


def AppTimer(func: Callable):
    """Provide the performance time of async function"""

    @functools.wraps(func)
    async def wrapper_timer(*args, **kwargs):
        """Calculate the performance time of an a sync function"""
        start_time = time.perf_counter()
        function_name = func.__name__
        module_name = (func.__code__.co_filename).rsplit("/", maxsplit=1)[-1]
        tag = f"[{module_name}]"

        value = await func(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time
        function = f"{rgb(function_name, 'royal')}{rgb('()', 'yellow')}"
        log.timer(f"{rgb(tag, 'green')}: {function} completed in {elapsed_time:0.7f}s")
        return value

    return wrapper_timer


def AppTimerSync(func: Callable):
    """Calculate the performance time of a sync function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        function_name = func.__name__
        module_name = (func.__code__.co_filename).rsplit("/", maxsplit=1)[-1]
        tag = f"[{module_name}]"

        value = func(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time
        function = f"{rgb(function_name, 'royal')}{rgb('()', 'yellow')}"
        log.timer(f"{rgb(tag, 'green')}: {function} completed in {elapsed_time:0.7f}s")
        return value

    return wrapper_timer
