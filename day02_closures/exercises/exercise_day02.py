"""Day 2 - Closures: hands-on exercise (Section 10).

Fill in each TODO yourself before checking the lesson's guidance again.
Do not look up a full solution before attempting all three parts.
"""

from typing import Callable


# --- Part A (basic) ---------------------------------------------------------
# Write make_running_average() that returns a function add(value: float) -> float.
# Each call to add() supplies a new number and returns the running average of
# all numbers supplied so far.
#
# Example:
#   avg = make_running_average()
#   avg(10)  # -> 10.0
#   avg(20)  # -> 15.0
#   avg(30)  # -> 20.0

def make_running_average() -> Callable[[float], float]:
    # TODO: implement using closure state (nonlocal total + count, or a list)
    total = 0
    count = 0

    def add(value: float) -> float:
        nonlocal total, count
        total += value
        count += 1
        return total / count

    return add


# --- Part B (intermediate) --------------------------------------------------
# Write make_event_bus() that returns a (subscribe, publish) pair of closures
# sharing private state:
#   subscribe(handler) registers a callback
#   publish(event) calls every registered handler with `event`
# No class, no global list -- all state lives in cells shared between the
# two closures.

def make_event_bus() -> tuple[Callable[[Callable], None], Callable[[object], None]]:
    # TODO: implement subscribe/publish sharing a private list of handlers
    handlers = []
    def subscribe(handler: Callable) -> None:
        handlers.append(handler)

    def publish(event: object) -> None:
        for handler in handlers:
            handler(event)
    return subscribe, publish



# --- Part C (project-style) --------------------------------------------------
# Write make_config_gate(get_flag) that returns a decorator-like closure
# guard(func). guard(func) returns a new function that only calls
# func(*args, **kwargs) if get_flag() currently returns True; otherwise it
# prints "blocked: feature disabled" and returns None.

def make_config_gate(get_flag: Callable[[], bool]) -> Callable[[Callable], Callable]:
    # TODO: implement guard(func) -> wrapped(*args, **kwargs)
    def guard(func: Callable) -> Callable:
        def wrapped(*args, **kwargs):
            if get_flag(): 
                return func(*args, **kwargs)
            else:
                print("blocked: feature disabled")
                return None
        return wrapped
    return guard


if __name__ == "__main__":
    # --- quick manual checks; expand with your own test cases ---
    avg = make_running_average()
    print(avg(10), avg(20), avg(30))  # expect 10.0 15.0 20.0

    subscribe, publish = make_event_bus()
    subscribe(lambda e: print(f"handler1 got: {e}"))
    subscribe(lambda e: print(f"handler2 got: {e}"))
    publish("user_created")

    flag = {"enabled": True}
    guard = make_config_gate(lambda: flag["enabled"])

    @guard
    def risky_operation():
        print("risky_operation ran")

    risky_operation()          # should run
    flag["enabled"] = False
    risky_operation()          # should be blocked
    flag["enabled"] = True
    risky_operation()          # should run
