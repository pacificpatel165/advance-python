"""
Day 3 -- Decorators: common mistakes, bad vs. better (Section 7).

Run: python common_mistakes.py
"""
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mistakes")


# --- Mistake 1: forgetting functools.wraps ---

def log_calls_bad(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def log_calls_better(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@log_calls_bad
def compute_total_bad(items):
    return sum(items)


@log_calls_better
def compute_total_better(items):
    return sum(items)


# --- Mistake 2: swallowing exceptions silently ---

def safe_bad(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None  # hides EVERYTHING, including real bugs
    return wrapper


def safe_better(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError):
            logger.exception("expected failure in %s", func.__name__)
            return None
        # anything else (e.g. TypeError from a real bug) propagates
    return wrapper


# --- Mistake 3: shared mutable state across all decorated functions ---

_shared_cache = {}


def memoize_bad(func):
    @wraps(func)
    def wrapper(*args):
        if args not in _shared_cache:
            _shared_cache[args] = func(*args)
        return _shared_cache[args]
    return wrapper


def memoize_better(func):
    cache = {}  # private per decorated function, via closure (Day 2)

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


if __name__ == "__main__":
    print("compute_total_bad.__name__    =", compute_total_bad.__name__)
    print("compute_total_better.__name__ =", compute_total_better.__name__)

    @safe_bad
    def divide_bad(a, b):
        return a / b

    @safe_better
    def divide_better(a, b):
        return a / b

    print("safe_bad on ZeroDivisionError:", divide_bad(1, 0))  # silently None
    try:
        divide_better(1, 0)  # ZeroDivisionError is not ValueError/KeyError -> propagates
    except ZeroDivisionError:
        print("safe_better correctly let ZeroDivisionError propagate")
