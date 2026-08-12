"""
Day 1 - Section 5.3: Real-world / project-oriented example
A small validation engine driven entirely by a registry of function objects --
this mirrors how real request-validation layers are structured.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class ValidationResult:
    field: str
    is_valid: bool
    message: str = ""


FieldValidator = Callable[[str, object], ValidationResult]


def required(field: str, value: object) -> ValidationResult:
    ok = value is not None and value != ""
    return ValidationResult(field, ok, "" if ok else f"{field} is required")


def max_length(limit: int) -> FieldValidator:
    """Higher-order function: configures and returns a validator."""

    def _check(field: str, value: object) -> ValidationResult:
        ok = isinstance(value, str) and len(value) <= limit
        message = "" if ok else f"{field} must be at most {limit} characters"
        return ValidationResult(field, ok, message)

    return _check


def run_validators(
    data: dict[str, object],
    rules: dict[str, list[FieldValidator]],
) -> list[ValidationResult]:
    """Applies each configured validator function to its field."""
    results: list[ValidationResult] = []
    for field, validators in rules.items():
        value = data.get(field)
        for validator in validators:
            results.append(validator(field, value))
    return results


if __name__ == "__main__":
    # Configuration: which functions apply to which field.
    rules: dict[str, list[FieldValidator]] = {
        "username": [required, max_length(20)],
        "bio": [max_length(280)],
    }

    payload = {"username": "prashant", "bio": "x" * 300}
    failures = [r for r in run_validators(payload, rules) if not r.is_valid]
    for failure in failures:
        print(failure.message)
    # bio must be at most 280 characters
