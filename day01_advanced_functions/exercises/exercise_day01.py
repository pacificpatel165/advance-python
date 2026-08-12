"""
Day 1 - Hands-On Exercise
Work through Part A, B, and C in order. Do not look up a solution first.
"""

from __future__ import annotations

from typing import Callable

from field_validation_engine import (  # if running standalone, copy the file in instead
    FieldValidator,
    ValidationResult,
    required,
    max_length,
    run_validators,
)


# --- Part A (basic) ----------------------------------------------------------
def apply_all(funcs: list[Callable[[int], int]], value: int) -> list[int]:
    """Apply each function in `funcs` to `value`; return the list of results."""
    # TODO: implement
    raise NotImplementedError


# --- Part B (intermediate) ---------------------------------------------------
def compose(*funcs: Callable) -> Callable:
    """
    Return a single function equivalent to applying `funcs` in sequence,
    right to left: compose(f, g)(x) == f(g(x))
    """
    # TODO: implement
    raise NotImplementedError


# --- Part C (project-style) ---------------------------------------------------
def one_of(allowed_values: list[str]) -> FieldValidator:
    """Return a validator that checks the field's value is in `allowed_values`."""
    # TODO: implement
    raise NotImplementedError


def combine(*validators: FieldValidator) -> FieldValidator:
    """
    Return a validator that runs each of `validators` in order and returns
    the FIRST failing ValidationResult, or a passing result if all succeed.
    """
    # TODO: implement
    raise NotImplementedError


if __name__ == "__main__":
    # Part A check
    print(apply_all([lambda x: x + 1, lambda x: x * 2, lambda x: x**2], 3))

    # Part B check
    print(compose(str, lambda x: x * 2)(5))  # expected: "10"

    # Part C check
    rules: dict[str, list[FieldValidator]] = {
        "role": [combine(required, one_of(["admin", "editor", "viewer"]))],
    }
    payload = {"role": "manager"}
    for result in run_validators(payload, rules):
        print(result)
