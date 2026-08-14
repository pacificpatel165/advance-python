"""Day 2 - Closures: basic example (Section 5.1)."""


def make_power(exponent: int):
    def power(base: float) -> float:
        return base ** exponent
    return power


def main() -> None:
    square = make_power(2)
    cube = make_power(3)
    print(square(5))  # 25
    print(cube(2))    # 8


if __name__ == "__main__":
    main()
