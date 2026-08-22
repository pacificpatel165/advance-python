"""Day 3 -- Decorators: deep-dive questions with runnable demonstrations."""
from functools import lru_cache, wraps


# ============================================================
# Question 1
# ============================================================

# Question Section:
# Given:
#     @a
#     @b
#     @c
#     def f(): ...
# write the equivalent nested assignment expression. If each outer decorator
# function prints its name, what order do those prints appear in at module load?

# Answer Section:
# The equivalent expression is `f = a(b(c(f)))`. Decoration is applied from
# the bottom upward, so c runs first, then b, then a. The output is:
# c
# b
# a
# This happens while the function is being defined, before f is called.

# Executable Independent Code Section:
def q1_demo():
    events = []

    def make_decorator(name):
        def decorator(func):
            events.append(name)
            return func

        return decorator

    a = make_decorator("a")
    b = make_decorator("b")
    c = make_decorator("c")

    def g():
        return "function result"

    f = a(b(c(g)))

    print("Q1 output:")
    print("equivalent expression: f = a(b(c(g)))")
    print("decoration order:", events)
    print("call result:", f())


q1_demo()
print()


# ============================================================
# Question 2
# ============================================================

# Question Section:
# What happens if a retry-style decorator swallows the last exception instead
# of re-raising it after all attempts are exhausted? What does calling code see,
# and why is this more dangerous than letting the exception propagate?

# Answer Section:
# Calling code receives `None` (or another accidental fallback value) and may
# continue as if the operation succeeded. The original failure and its traceback
# are lost, so callers cannot reliably distinguish success from failure. This
# can cause invalid data to be stored or later operations to fail far from the
# real cause. A retry decorator should re-raise the final exception.

# Executable Independent Code Section:
def q2_demo():
    def broken_retry(max_attempts):
        def decorator(func):
            @wraps(func)
            def wrapper():
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func()
                    except RuntimeError as exc:
                        print(f"attempt {attempt} failed: {exc}")
                # Bug: the final exception is swallowed and None is returned.

            return wrapper

        return decorator

    @broken_retry(max_attempts=2)
    def always_fails():
        raise RuntimeError("service unavailable")

    result = always_fails()
    print("Q2 output:")
    print("caller observed:", result)
    print("danger: None looks like a result, not a failure")


q2_demo()
print()


# ============================================================
# Question 3
# ============================================================

# Question Section:
# If wrapper accepts only *args and not **kwargs, what category of bugs appears,
# and who experiences them?

# Answer Section:
# Any future caller that invokes the decorated function with keyword arguments
# gets a TypeError from the wrapper, even when the original function supports
# those keywords. The decorator author introduced the defect, but every caller
# using keyword arguments experiences it. A general-purpose wrapper should pass
# both `*args` and `**kwargs` through.

# Executable Independent Code Section:
def q3_demo():
    def missing_keyword_support(func):
        @wraps(func)
        def wrapper(*args):
            return func(*args)

        return wrapper

    @missing_keyword_support
    def greet(name, punctuation="!"):
        return f"Hello, {name}{punctuation}"

    print("Q3 output:")
    print("positional call:", greet("Ada"))
    try:
        print("keyword call:", greet("Ada", punctuation="."))
    except TypeError as exc:
        print("keyword call failed:", exc)


q3_demo()
print()


# ============================================================
# Question 4
# ============================================================

# Question Section:
# How would you write unwrap_all(f) to follow __wrapped__ links until it finds
# the original undecorated function at the bottom of an arbitrary stack?

# Answer Section:
# Start with the supplied callable and repeatedly replace it with its
# `__wrapped__` attribute while that attribute exists. Returning the final object
# gives the original function. The seen-set below also prevents an accidental
# manually-created cycle from causing an infinite loop.

# Executable Independent Code Section:
def unwrap_all(function):
    seen = set()
    while hasattr(function, "__wrapped__") and id(function) not in seen:
        seen.add(id(function))
        function = function.__wrapped__
    return function


def q4_demo():
    def marker(label):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            wrapper.layer = label
            return wrapper

        return decorator

    @marker("outer")
    @marker("inner")
    def original(value):
        """Return the supplied value."""
        return value

    unwrapped = unwrap_all(original)
    print("Q4 output:")
    print("decorated name:", original.__name__)
    print("original name:", unwrapped.__name__)
    print("original docstring:", unwrapped.__doc__)
    print("original result:", unwrapped(42))


q4_demo()
print()


# ============================================================
# Question 5
# ============================================================

# Question Section:
# Why can an outermost cache suppress an inner logging or authorization
# decorator? What would a user see on the second call with identical arguments?

# Answer Section:
# The outer cache receives the call first. On a cache hit it returns the saved
# value immediately and never calls the inner decorator. Therefore the second
# identical call produces no inner log entry and does not repeat inner checks.
# This is useful for avoiding repeated work, but dangerous if the inner behavior
# must run on every call, such as authorization or auditing.

# Executable Independent Code Section:
def q5_demo():
    log = []

    def log_calls(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log.append(f"logged call: {args}")
            return func(*args, **kwargs)

        return wrapper

    @lru_cache(maxsize=None)
    @log_calls
    def square(number):
        return number * number

    first = square(5)
    second = square(5)  # This call hits the cache and does not log.

    print("Q5 output:")
    print("results:", first, second)
    print("log entries:", log)
    print("second call logged:", len(log) == 2)


q5_demo()