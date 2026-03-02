import time
import functools
import os

def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        t1 = time.perf_counter()

        filename = os.path.splitext(os.path.basename(func.__code__.co_filename))[0].upper()
        print(f"[{filename}:{func.__name__.upper()}] {(t1 - t0):.3f}s")

        return result
    return wrapper