"""Day 2 - Closures: advanced challenge (Section 11).

Build a debounced dispatcher using only closures + first-class functions.
Do not look up a full solution before attempting this yourself.
"""

from typing import Callable


def make_debouncer(min_interval_seconds: float, clock: Callable[[], float]) -> Callable:
    """
    Returns a decorator-like function `debounce(func)`.

    debounce(func) returns a new callable `guarded(*args, **kwargs)` that:
      - calls func(*args, **kwargs) and returns its result IF at least
        `min_interval_seconds` have passed (according to `clock()`) since
        the last time func actually ran through this guarded wrapper,
      - otherwise does NOT call func, and instead returns the LAST
        successful result without recomputing anything.

    `clock` is injected (rather than calling time.time() directly) so the
    behavior is deterministic and testable.
    """
    if min_interval_seconds < 0:
        raise ValueError("min_interval_seconds must be non-negative")

    def debounce(func: Callable) -> Callable:
        if func is None:
            raise ValueError("func must be a callable")

        last_call_time = -float("inf")
        last_result = None

        def guarded(*args, **kwargs):
            nonlocal last_call_time, last_result
            current_time = clock()
            if current_time - last_call_time >= min_interval_seconds:
                last_result = func(*args, **kwargs)
                last_call_time = current_time
            return last_result
        return guarded
    return debounce


def make_fake_clock() -> tuple[Callable[[float], None], Callable[[], float]]:
    """
    Returns (advance, clock):
      - clock() returns the current fake time (starts at 0.0)
      - advance(seconds) moves the fake clock forward deterministically
    Use this in your test instead of real time.sleep().
    """
    current_time = 0.0

    def advance(seconds: float) -> None:
        nonlocal current_time
        current_time += seconds

    def clock() -> float:
        return current_time
    
    return advance, clock


if __name__ == "__main__":
    advance, clock = make_fake_clock()
    debounce = make_debouncer(min_interval_seconds=5.0, clock=clock)

    call_count = [0]

    @debounce
    def do_work():
        call_count[0] += 1
        return f"ran #{call_count[0]}"

    print(do_work())   # should actually run -> "ran #1"
    print(do_work())   # too soon -> returns "ran #1" again, no new call
    advance(5.0)
    print(do_work())   # interval passed -> actually runs -> "ran #2"
