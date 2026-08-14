"""
Day 3 -- Decorators: hands-on exercise (Section 10 of the lesson).

Implement Parts A, B, and C yourself. Do not look up a solution first.
Each part builds on Days 1-2 (higher-order functions, closures) plus today's
decorator patterns.
"""
from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar
import inspect

F = TypeVar("F", bound=Callable[..., object])


# --- Part A (basic) ---------------------------------------------------------
# Write a decorator `log_arguments` that prints the decorated function's
# name, its positional args, and its keyword args every time it's called,
# then calls through to the original function and returns its result
# unchanged. Use functools.wraps.

def log_arguments(func: F) -> F:
    """TODO: implement."""
    raise NotImplementedError


# --- Part B (intermediate) --------------------------------------------------
# Write a decorator factory `validate_positive(*param_names)` that, given
# the names of parameters that must be positive numbers, raises ValueError
# BEFORE calling the wrapped function if any named argument (found via
# inspect.signature(func).bind(...)) is <= 0.
#
# Test on something like:
#   @validate_positive("amount", "tax")
#   def charge_card(amount: float, tax: float) -> float: ...

def validate_positive(*param_names: str) -> Callable[[F], F]:
    """TODO: implement."""
    raise NotImplementedError


# --- Part C (project-style) --------------------------------------------------
# Write a decorator `cache_with_ttl(seconds, clock)` that memoizes a
# single-argument function's results, but treats a cached entry as expired
# (and recomputes) once `seconds` have passed since it was stored, using the
# injected `clock` rather than time.time() directly. Store (value, stored_at)
# per cache key.

def cache_with_ttl(seconds: float, clock: Callable[[], float]) -> Callable[[F], F]:
    """TODO: implement."""
    raise NotImplementedError


if __name__ == "__main__":
    # --- quick manual checks; replace/extend as you implement each part ---

    # Part A
    # @log_arguments
    # def add(a, b): return a + b
    # add(2, 3)

    # Part B
    # @validate_positive("amount", "tax")
    # def charge_card(amount: float, tax: float) -> float:
    #     return amount + tax
    # charge_card(10, 2)
    # charge_card(-5, 2)  # should raise ValueError

    # Part C
    # def make_fake_clock():
    #     t = [0.0]
    #     def advance(seconds): t[0] += seconds
    #     def clock(): return t[0]
    #     return advance, clock
    #
    # advance, clock = make_fake_clock()
    # calls = []
    # @cache_with_ttl(seconds=10, clock=clock)
    # def expensive(n):
    #     calls.append(n)
    #     return n * n
    # expensive(5); expensive(5)   # second call should be a cache hit
    # advance(11)
    # expensive(5)                 # should recompute after TTL expiry
    # print(calls)  # expect two entries: [5, 5]

    pass
