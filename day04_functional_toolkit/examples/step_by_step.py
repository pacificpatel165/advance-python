"""
Day 4 -- Functional Programming Toolkit: step-by-step walkthrough (Section 2 of the lesson).
Run directly: python step_by_step.py
"""
from __future__ import annotations

from functools import partial, reduce, singledispatch
from itertools import chain, groupby, islice
from operator import add


def power(base: float, exponent: float) -> float:
    return base**exponent


def demo_partial() -> None:
    square = partial(power, exponent=2)
    cube = partial(power, exponent=3)
    print("partial:", square(5), cube(5))


def demo_reduce() -> None:
    numbers = [1, 2, 3, 4, 5]
    total = reduce(lambda acc, x: acc + x, numbers, 0)
    print("reduce (lambda):", total)

    total_via_operator = reduce(add, numbers, 0)
    print("reduce (operator.add):", total_via_operator)


@singledispatch
def describe(value: object) -> str:
    return f"a generic value: {value!r}"


@describe.register
def _(value: int) -> str:
    return f"an integer: {value}"


@describe.register
def _(value: list) -> str:
    return f"a list of {len(value)} items"


def demo_singledispatch() -> None:
    print("singledispatch:", describe(42))
    print("singledispatch:", describe([1, 2, 3]))
    print("singledispatch:", describe(3.14))


def demo_itertools() -> None:
    first_three = list(islice(range(1_000_000), 3))
    print("islice:", first_three)

    combined = list(chain([1, 2], [3, 4], [5]))
    print("chain:", combined)

    data = [("a", 1), ("a", 2), ("b", 3)]
    for key, group in groupby(data, key=lambda pair: pair[0]):
        print("groupby:", key, list(group))


if __name__ == "__main__":
    demo_partial()
    demo_reduce()
    demo_singledispatch()
    demo_itertools()
