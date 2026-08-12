# ================================================================================
# QUESTION 1
# ================================================================================
# Given make_multiplier from Section 2, if you call make_multiplier(2) three
# separate times and store the results in a, b, c, are a, b, and c the same 
# function object, or three distinct ones? Why?

# ANSWER:
# Three DISTINCT function objects. Each call to make_multiplier() creates a
# NEW function object with its own closure scope. They behave the same
# (a(5) == b(5) == 10) but are NOT the same object in memory (a is not b).
# 
# Demo:
def make_multiplier(factor: int):
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

a = make_multiplier(2)
b = make_multiplier(2)
print(a is b)  # False - different objects


# ================================================================================
# QUESTION 2
# ================================================================================
# Predict the output:
def outer():
    funcs = [lambda: x for x in range(3)]
    return funcs
for f in outer():
    print(f())

# ANSWER:
# Output: 2, 2, 2
#
# Why? ALL lambdas capture the SAME variable 'x' by REFERENCE, not by value.
# When the list comprehension finishes, x=2 (last value). When you call each
# lambda, they ALL look up 'x' and find x=2.
#
# FIX (capture by value):
# funcs = [lambda y=x: y for x in range(3)]  # Default arg captures at definition
# This produces: 0, 1, 2 (each lambda has its own value frozen as default)

# ================================================================================


# ================================================================================
# QUESTION 3
# ================================================================================
# sorted(items, key=str.upper) works even though str.upper looks like 
# "just a method." What is str.upper actually referring to when used this 
# way, and why does passing it as key work correctly for each string in items?

# ANSWER:
# str.upper is a METHOD REFERENCE (unbound method), not a function call.
# It's a callable that takes a string and returns its uppercase version.
#
# How it works:
# - sorted() calls str.upper(item) for each item:
#   str.upper("apple")   → "APPLE"
#   str.upper("BANANA")  → "BANANA"
#   str.upper("Cherry")  → "CHERRY"
# - Sorts by these uppercase versions
#
# Comparison:
# sorted(items, key=str.upper)           ← method reference (works!)
# sorted(items, key=lambda x: x.upper()) ← anonymous function (works!)
items = ["apple", "BANANA", "Cherry"]
# This:
sorted(items, key=str.upper)
# Is equivalent to:
sorted(items, key=lambda x: x.upper())
# sorted(items, key=str.upper())         ← ERROR: needs an argument

# ================================================================================


# ================================================================================
# QUESTION 4
# ================================================================================
# If a function f is passed into another function g and g never calls f,
# only stores it, does f's code ever execute? What does this imply about
# the difference between "passing a function" and "running a function"?

# ANSWER:
# NO, f's code never executes when passed to g (without calling it).
#
# Key distinction:
# Passing:  g(f)      → passes function object, code does NOT run
# Calling:  g(f())    → calls f first, THEN passes the result
#           f()       → executes the function
#
def f():
    print("F IS RUNNING!")
    return 42

def g(func):
    # Just store it, never call it
    return func  # Return the function object, unchanged

result = g(f)  # Pass f to g
# Nothing printed! f's code never ran.

print(result)  # <function f at 0x...>
result()       # NOW it runs: F IS RUNNING!

# This implies:
# - Functions are FIRST-CLASS VALUES (data)
# - You can store, pass, and delay execution
# - Function reference is just data until you call it with ()
# - This enables: higher-order functions, callbacks, event handlers,
#   task scheduling (call the function LATER, not immediately)

# ================================================================================


# ================================================================================
# QUESTION 5
# ================================================================================
# Why does the "better" fix in Mistake 2 (lambda i=i: print(i)) work, in
# terms of when default argument values are evaluated versus when the lambda
# body's free variables are looked up?

# ANSWER:
# DEFAULT ARGUMENTS are evaluated ONCE at function DEFINITION time.
# FREE VARIABLES are looked up at function CALL time.
#
# BROKEN (without default argument):
# for i in range(3):
#     funcs.append(lambda: print(i))
# Result: prints 2, 2, 2 (all look up same variable i)
#
# FIXED (with default argument):
# for i in range(3):
#     funcs.append(lambda i=i: print(i))
# Result: prints 0, 1, 2 (each has frozen default value)
#
# Why FIXED works:
# - lambda i=i: the right 'i' is evaluated AT DEFINITION TIME
# - This "freezes" the current value as the default parameter
# - At CALL TIME, each lambda uses its own default, not shared variable
#
# Key difference:
# - lambda: print(i)      ← 'i' is looked up at call time (late binding)
# - lambda i=i: print(i)  ← 'i' is captured at definition time (early binding)