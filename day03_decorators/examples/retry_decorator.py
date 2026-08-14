"""
Day 3 -- Decorators: intermediate example, a decorator factory (Section 5.2).

Run: python retry_decorator.py
"""
from functools import wraps
from typing import Callable, TypeVar
import time

F = TypeVar("F", bound=Callable[..., object])


def retry(max_attempts: int, delay_seconds: float = 0.0) -> Callable[[F], F]:
    """Decorator factory: retries a function on exception, up to max_attempts."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    print(f"attempt {attempt} failed: {exc!r}")
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)
            assert last_exc is not None
            raise last_exc
        return wrapper  # type: ignore[return-value]
    return decorator


_flaky_calls = 0


@retry(max_attempts=3)
def flaky() -> str:
    global _flaky_calls
    _flaky_calls += 1
    if _flaky_calls < 3:
        raise ConnectionError("simulated network failure")
    return "success"


if __name__ == "__main__":
    print(flaky())
