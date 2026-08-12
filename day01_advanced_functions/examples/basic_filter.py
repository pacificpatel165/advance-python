"""
Day 1 - Section 5.1: Basic example
`filter` takes a named predicate as a value -- the smallest demonstration
of "function as argument."
"""


def is_even(n: int) -> bool:
    return n % 2 == 0


numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(is_even, numbers))
print(evens)  # [2, 4, 6]
