"""
Day 3 -- Decorators: real-world/project-oriented example (Section 5.3).

Demonstrates stacked decorators: an auth-check decorator factory
(@require_role) combined with a logging/timing decorator (@log_and_time),
mirroring a service-layer pattern used in web frameworks and internal APIs.

Run: python service_layer_guards.py
"""
from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("api")
F = TypeVar("F", bound=Callable[..., object])


class AuthorizationError(Exception):
    """Raised when the current caller lacks the required role."""


def require_role(role: str) -> Callable[[F], F]:
    """
    Decorator factory used on service-layer functions. Expects the wrapped
    function's first positional argument to be a `context` object exposing
    `context.user_role`.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(context, *args, **kwargs):
            if context.user_role != role:
                logger.warning(
                    "authorization denied: user_role=%r required=%r func=%s",
                    context.user_role, role, func.__name__,
                )
                raise AuthorizationError(f"requires role '{role}'")
            return func(context, *args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator


def log_and_time(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info("start %s", func.__name__)
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception("error in %s", func.__name__)
            raise
        else:
            elapsed = time.perf_counter() - start
            logger.info("done %s in %.4fs", func.__name__, elapsed)
            return result
    return wrapper  # type: ignore[return-value]


class RequestContext:
    def __init__(self, user_role: str) -> None:
        self.user_role = user_role


@log_and_time
@require_role("admin")
def delete_user(context: RequestContext, user_id: int) -> str:
    return f"user {user_id} deleted"


if __name__ == "__main__":
    try:
        delete_user(RequestContext(user_role="viewer"), 42)
    except AuthorizationError as exc:
        print(f"blocked: {exc}")

    print(delete_user(RequestContext(user_role="admin"), 42))
