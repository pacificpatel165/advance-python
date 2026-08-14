"""
Day 3 -- Decorators: advanced challenge (Section 11 of the lesson).

Build a composable middleware pipeline out of ordinary decorators.
Do not look up a solution first.
"""
from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])


def compose_decorators(*decorators: Callable[[F], F]) -> Callable[[F], F]:
    """
    Returns a single decorator that applies the given decorators, in the
    order listed (leftmost decorator ends up OUTERMOST, i.e. it runs first
    on every call), equivalent to stacking them individually with @.

    compose_decorators(log_and_time, require_role("admin"))
    applied to a function should behave identically to:

        @log_and_time
        @require_role("admin")
        def f(...): ...

    TODO: implement. Think carefully about fold direction -- the first
    decorator in the argument list must end up OUTERMOST.
    """
    raise NotImplementedError


if __name__ == "__main__":
    # Reuse (or re-import) `log_and_time` and `require_role` from
    # examples/service_layer_guards.py to build both:
    #   1. a manually stacked version:  @log_and_time \n @require_role("admin")
    #   2. a composed version:          @compose_decorators(log_and_time, require_role("admin"))
    # on two separate copies of the same underlying function, then assert
    # both produce identical behavior for an authorized and an unauthorized
    # call (same exceptions raised, same log order).
    pass
