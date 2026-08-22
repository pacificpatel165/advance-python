"""
Day 4 -- Functional Programming Toolkit: common mistakes, bad vs. better (Section 7 of the lesson).
Run directly: python common_mistakes.py
"""
from __future__ import annotations

from functools import reduce
from operator import itemgetter


def bad_reduce_for_sum(prices: list[float]) -> float:
    """MISTAKE: reduce() for a fold that a builtin already expresses better."""
    return reduce(lambda acc, x: acc + x, prices, 0)


def better_sum(prices: list[float]) -> float:
    """BETTER: use the builtin -- clearer, faster, more idiomatic."""
    return sum(prices)


def bad_sort_key(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """MISTAKE: a lambda that just forwards to indexing."""
    return sorted(records, key=lambda record: record[1])


def better_sort_key(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """BETTER: operator.itemgetter -- clearer intent, C-fast."""
    return sorted(records, key=itemgetter(1))


if __name__ == "__main__":
    prices = [9.99, 4.5, 12.0]
    assert bad_reduce_for_sum(prices) == better_sum(prices)
    print("sum equivalence OK:", better_sum(prices))

    records = [("b", 2), ("a", 3), ("c", 1)]
    assert bad_sort_key(records) == better_sort_key(records)
    print("sort equivalence OK:", better_sort_key(records))
