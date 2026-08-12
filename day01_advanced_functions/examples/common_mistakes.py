"""
Day 1 - Section 7: Common Mistakes
Bad-vs-better pairs. Run this file and read the comments.
"""

# --- Mistake 1: calling the function when you meant to pass it -------------

def handle_click() -> None:
    print("clicked!")


def on_click_bad(callback_result) -> None:
    # `callback_result` here is whatever handle_click() returned (None),
    # not a callable -- calling it later would raise TypeError.
    print(f"registered: {callback_result!r}")


def on_click_good(callback) -> None:
    callback()  # callback is the function object itself; call it when needed


on_click_bad(handle_click())   # BAD: calls handle_click immediately
on_click_good(handle_click)    # BETTER: passes the function object itself


# --- Mistake 2: late-binding closures over loop variables -------------------

# BAD: all three functions print 2, not 0, 1, 2
funcs_bad = [lambda: print(i) for i in range(3)]
print("bad:")
for f in funcs_bad:
    f()  # 2, 2, 2

# BETTER: bind the value at creation time via a default argument
funcs_good = [lambda i=i: print(i) for i in range(3)]
print("good:")
for f in funcs_good:
    f()  # 0, 1, 2
