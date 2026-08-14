"""Day 2 - Closures: intermediate example (Section 5.2)."""

from typing import Callable


def make_rate_limiter(max_calls: int) -> Callable[[], bool]:
    """Returns a function that reports True if a call is still allowed."""
    calls_made = 0

    def allow_call() -> bool:
        nonlocal calls_made
        if calls_made >= max_calls:
            return False
        calls_made += 1
        return True

    return allow_call


def main() -> None:
    limiter = make_rate_limiter(3)
    results = [limiter() for _ in range(5)]
    print(results)  # [True, True, True, False, False]


if __name__ == "__main__":
    main()
