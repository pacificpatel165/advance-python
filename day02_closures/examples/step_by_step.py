"""Day 2 - Closures: step-by-step intuition build.

Run: python step_by_step.py
"""


def make_greeter(greeting: str):
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"
    return greet


def make_counter():
    count = 0

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment


def main() -> None:
    hello = make_greeter("Hello")
    print(hello("Prashant"))  # Hello, Prashant!

    print(hello.__closure__)
    print(hello.__closure__[0].cell_contents)
    print(hello.__code__.co_freevars)

    counter = make_counter()
    print(counter())  # 1
    print(counter())  # 2
    print(counter())  # 3

    counter_a = make_counter()
    counter_b = make_counter()
    print(counter_a())  # 1
    print(counter_a())  # 2
    print(counter_b())  # 1 -- independent state


if __name__ == "__main__":
    main()
