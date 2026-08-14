"""Day 2 - Closures: common mistakes, bad vs. better (Section 7)."""


# --- Mistake 1: forgetting `nonlocal` -------------------------------------

def make_counter_bad():
    count = 0

    def increment():
        count += 1  # UnboundLocalError: `count` is treated as local here
        return count

    return increment


def make_counter_better():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


# --- Mistake 2: loop-capture bug -------------------------------------------

def bad_loop_capture():
    handlers = []
    for i in range(3):
        def handler():
            return i
        handlers.append(handler)
    return [h() for h in handlers]  # [2, 2, 2]


def better_loop_capture():
    handlers = []
    for i in range(3):
        def handler(i=i):
            return i
        handlers.append(handler)
    return [h() for h in handlers]  # [0, 1, 2]


# --- Mistake 3: closing over a mutable object you keep mutating ------------

def demo_live_reference():
    config = {"debug": False}

    def make_logger():
        def log(msg: str):
            if config["debug"]:
                print(f"[DEBUG] {msg}")
        return log

    logger = make_logger()
    config["debug"] = True  # logger sees this -- captured by reference
    logger("test")          # prints, because config is shared, not snapshotted


def main() -> None:
    counter = make_counter_better()
    print(counter(), counter(), counter())  # 1 2 3

    try:
        make_counter_bad()()
    except UnboundLocalError as exc:
        print(f"Expected error: {exc}")

    print("bad_loop_capture:", bad_loop_capture())
    print("better_loop_capture:", better_loop_capture())

    demo_live_reference()


if __name__ == "__main__":
    main()
