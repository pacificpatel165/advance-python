"""
Day 1 - Hands-On Exercise
Work through Part A, B, and C in order. Do not look up a solution first.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

# Make the sibling `examples/` folder importable regardless of cwd or how this
# file is invoked (plain `python3 path/to/exercise_day01.py`, not `python -m`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from field_validation_engine import (  # noqa: E402
    FieldValidator,
    ValidationResult,
    required,
    run_validators,
)


# --- Part A (basic) ----------------------------------------------------------
def apply_all(funcs: list[Callable[[int], int]], value: int) -> list[int]:
    """Apply each function in `funcs` to `value`; return the list of results."""
    return [f(value) for f in funcs]


# --- Part B (intermediate) ---------------------------------------------------
def compose(*funcs: Callable) -> Callable:
    """
    Return a single function equivalent to applying `funcs` in sequence,
    right to left: compose(f, g)(x) == f(g(x))
    """
    def xcomposed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return xcomposed


# --- Part C (project-style) ---------------------------------------------------
def one_of(allowed_values: list[str]) -> FieldValidator:
    """Return a validator that checks the field's value is in `allowed_values`."""
    def _check(field: str, value: object) -> ValidationResult:
        ok = value in allowed_values
        message = "" if ok else f"{field} must be one of {allowed_values}"
        return ValidationResult(field, ok, message)

    return _check


def combine(*validators: FieldValidator) -> FieldValidator:
    """
    Return a validator that runs each of `validators` in order and returns
    the FIRST failing ValidationResult, or a passing result if all succeed.
    """
    def _check(field: str, value: object) -> ValidationResult:
        for validator in validators:
            result = validator(field, value)
            if not result.is_valid:
                return result
        return ValidationResult(field, True, "")

    return _check


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
