import time
import functools
import os
import threading
from config import DebugConfig

def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not DebugConfig.BENCHMARK:
            return func(*args, **kwargs)
        
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()

        filename = os.path.splitext(os.path.basename(func.__code__.co_filename))[0].upper()
        thread_name = threading.current_thread().name.upper()

        print(
            f"[{thread_name}] [{filename}:{func.__name__.upper()}] {(t1 - t0):.3f}s",
            flush=True
        )

        return result
    return wrapper