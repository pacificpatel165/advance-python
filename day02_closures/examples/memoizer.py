"""Day 2 - Closures: real-world/project-oriented example (Section 5.3)."""

from __future__ import annotations

import time
from typing import Callable

Number = float


def make_memoizer() -> tuple[Callable, Callable[[Callable], Callable]]:
    """
    Returns a (stats, memoize) pair. `memoize` wraps any single-argument
    function with a private cache closure; `stats` reports hit/miss counts
    for whichever function was wrapped, without exposing the cache dict.
    """
    hits = 0
    misses = 0

    def memoize(func: Callable[[Number], Number]) -> Callable[[Number], Number]:
        cache: dict[Number, Number] = {}

        def wrapped(n: Number) -> Number:
            nonlocal hits, misses
            if n in cache:
                hits += 1
                return cache[n]
            misses += 1
            result = func(n)
            cache[n] = result
            return result

        return wrapped

    def stats() -> dict[str, int]:
        return {"hits": hits, "misses": misses}

    return stats, memoize


def slow_square(n: Number) -> Number:
    time.sleep(0.01)  # simulate expensive work
    return n * n


def main() -> None:
    get_stats, memoize = make_memoizer()
    fast_square = memoize(slow_square)

    for value in [2, 2, 4, 2, 2, 3]:
        fast_square(value)

    print(get_stats())  # {'hits': 3, 'misses': 3}


if __name__ == "__main__":
    main()
