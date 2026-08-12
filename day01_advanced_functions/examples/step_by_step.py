"""
Day 1 - Section 2: Build Intuition
Four-step progression showing that a function is just a value.
"""


def shout(text: str) -> str:
    return text.upper() + "!"


# Step 1: a function is a value you can pass around.
my_func = shout          # no parentheses: referencing, not calling
print(my_func("hi"))     # HI!


# Step 2: a function can be stored in a collection.
operations = {
    "shout": shout,
    "whisper": lambda text: text.lower(),
}
print(operations["shout"]("careful"))  # CAREFUL!
print(operations["whisper"]("CAREFUL"))  # careful

# Step 3: a function can accept another function.
def apply_twice(func, value):
    return func(func(value))


print(apply_twice(shout, "hi"))  # HI!!


# Step 4: a function can build and return another function.
def make_multiplier(factor: int):
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier  # returning a function object, not calling it


double = make_multiplier(2)   # 2 is passed as 'factor'
triple = make_multiplier(3)   # 3 is passed as 'factor'
print(double(5), triple(5))   # 5 is passed as 'x'