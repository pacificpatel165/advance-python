"""
Day 4 -- Functional Programming Toolkit: hands-on exercise (Section 10 of the lesson).

Fill in each TODO. Do not look up a full solution first -- attempt each part,
then run this file directly to check your work against the asserts.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import partial, reduce, singledispatch
from itertools import chain, islice
from operator import add, mul
from typing import Any, Callable, Iterable, Iterator


# ---------------------------------------------------------------------------
# 1. Use functools.partial (not a hand-written closure) to build a multiplier.
# ---------------------------------------------------------------------------
def multiply(x: float, y: float) -> float:
    return x * y


def make_multiplier(factor: float) -> Callable[[float], float]:
    """
    TODO: return a callable equivalent to `lambda x: multiply(x, factor)`,
    built using functools.partial -- not a hand-written inner function.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 2. Fold-based total using functools.reduce + operator, contrasted with sum().
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class InventoryItem:
    name: str
    unit_price_cents: int
    quantity: int


def total_inventory_value_via_reduce(items: list[InventoryItem]) -> int:
    """
    TODO: compute the total value (sum of unit_price_cents * quantity for
    every item) using functools.reduce and operator.add/operator.mul.
    Do NOT use sum() or a list comprehension here -- that's the point of
    this part of the exercise.
    """
    raise NotImplementedError


def total_inventory_value_via_sum(items: list[InventoryItem]) -> int:
    """TODO: compute the same total using sum() (or a comprehension). Compare readability."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 3. singledispatch-based renderer for a CLI report.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Money:
    cents: int

    def __str__(self) -> str:
        return f"${self.cents / 100:.2f}"


@singledispatch
def render(value: Any) -> str:
    """
    TODO: default/fallback case. Unregistered types should raise TypeError
    with a clear message, NOT silently guess a formatting.
    """
    raise NotImplementedError


# TODO: register handlers for int, float, str, list, and Money below using
# @render.register, each producing a distinct, sensible string format.


# ---------------------------------------------------------------------------
# 4. Pagination built on itertools.islice + itertools.chain.from_iterable.
# ---------------------------------------------------------------------------
def paginate(iterable: Iterable[Any], page_size: int) -> Iterator[list[Any]]:
    """TODO: yield consecutive pages (lists) of at most `page_size` items each."""
    raise NotImplementedError


def flatten_pages(pages: Iterable[list[Any]]) -> Iterator[Any]:
    """TODO: reconstruct the original flat sequence from paginate()'s output."""
    raise NotImplementedError


if __name__ == "__main__":
    # --- Part 1 ---
    double = make_multiplier(2)
    assert double(21) == 42

    # --- Part 2 ---
    items = [
        InventoryItem("widget", 250, 4),
        InventoryItem("gadget", 999, 2),
    ]
    assert total_inventory_value_via_reduce(items) == total_inventory_value_via_sum(items)

    # --- Part 3 ---
    assert render(42) != render("42")
    try:
        render(object())
    except TypeError:
        pass
    else:
        raise AssertionError("render() should raise TypeError for unregistered types")

    # --- Part 4 ---
    original = list(range(23))
    pages = list(paginate(original, page_size=5))
    assert all(len(page) <= 5 for page in pages)
    assert list(flatten_pages(pages)) == original

    print("All checks passed.")
