"""
Day 3 -- Decorators: step-by-step build-up (Section 2 of the lesson).

Run: python step_by_step.py
"""
from functools import wraps


# Step 1 -- manual wrapping, no @ syntax yet
def shout(text: str) -> str:
    return text.upper()


def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__} with {args}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper


shout = add_logging(shout)


# Step 2 -- same thing, with @ syntax
@add_logging
def shout2(text: str) -> str:
    return text.upper()


# Step 3 -- preserving identity with functools.wraps
def add_logging_wrapped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__} with {args}")
        return func(*args, **kwargs)
    return wrapper


@add_logging_wrapped
def shout3(text: str) -> str:
    """Uppercase the given text."""
    return text.upper()


# Step 4 -- a decorator factory (decorator that takes arguments)
def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(times=3)
def ping() -> None:
    print("ping")


if __name__ == "__main__":
    print("--- Step 1: manual decoration ---")
    shout("hello")

    print("\n--- Step 2: @ syntax ---")
    shout2("hi there")

    print("\n--- Step 3: identity preserved ---")
    shout3("hey")
    print("shout3.__name__ =", shout3.__name__)
    print("shout3.__doc__  =", shout3.__doc__)

    print("\n--- Step 4: decorator factory ---")
    ping()
