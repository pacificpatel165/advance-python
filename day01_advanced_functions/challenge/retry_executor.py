"""
Day 1 - Advanced Challenge
A retry-with-backoff executor built purely from functions-as-values.
Do not look up a solution before attempting this yourself.
"""

from __future__ import annotations

from typing import Callable


def retry(
    func: Callable[[], object],
    attempts: int,
    should_retry: Callable[[Exception], bool],
) -> object:
    """
    Calls func() up to `attempts` times.
    - If func() succeeds, return its result immediately.
    - If func() raises an exception, only retry when should_retry(exception) is True.
    - If retries are exhausted or should_retry returns False, re-raise the last exception.
    """
    def _retry(attempts_remaining: int) -> object:
        try:
            return func()
        except Exception as e:
            if attempts_remaining <= 1 or not should_retry(e):
                raise
            return _retry(attempts_remaining - 1)
    return _retry(attempts)
  

    # # TODO: implement
    # raise NotImplementedError


if __name__ == "__main__":
    # TODO: simulate a flaky operation, e.g. using a counter in enclosing scope
    # that fails the first two times and succeeds on the third call.
    #
    # Example skeleton:
    #
    def make_flaky_operation():
        call_count = 0
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError(f"attempt {call_count} failed")
            return "success"
        return operation
    
    flaky = make_flaky_operation()
    try:
        result = retry(flaky, attempts=3, should_retry=lambda e: isinstance(e, ConnectionError))
        print(result)
    except Exception as e:
        print(f"Operation failed after retries: {e}")
    # pass
