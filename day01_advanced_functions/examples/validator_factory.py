"""
Day 1 - Section 5.2: Intermediate example
A higher-order function that configures and returns a validator function.
"""

from typing import Callable


def build_validator(min_length: int, max_length: int) -> Callable[[str], bool]:
    """Returns a function that validates a string's length range."""

    def validate(value: str) -> bool:
        return min_length <= len(value) <= max_length

    return validate


username_rule = build_validator(3, 20)
password_rule = build_validator(8, 64)

print(username_rule("ab"))       # False
print(password_rule("hunter2"))  # False (too short)
