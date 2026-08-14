"""
Day 3 -- Decorators: basic example (Section 5.1).

Run: python basic_timed.py
"""
from functools import wraps
import time


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


@timed
def slow_add(a: int, b: int) -> int:
    time.sleep(0.05)
    return a + b


if __name__ == "__main__":
    print(slow_add(2, 3))
