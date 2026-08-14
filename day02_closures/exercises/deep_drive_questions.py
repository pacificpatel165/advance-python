# ============================================================
# Question 1
# ============================================================

# Question Section:
# In the make_memoizer example, hits and misses are free variables in two different
# inner functions, defined in two different def blocks. Are they sharing the same cell,
# or does each inner function get its own? How would you verify this using __closure__?

# Answer Section:
# They share the same outer cell. Both nested functions close over the same
# outer variables defined in make_memoizer(). The __closure__ attribute shows the
# captured free variables. If they were different cells, each function would have
# independent state. Here, both functions refer to the same shared hits and misses.

# Executable Independent Code Section:
def q1_demo():
    def make_memoizer():
        hits = 0
        misses = 0

        def memoize():
            nonlocal hits, misses
            hits += 1
            return hits

        def stats():
            return {"hits": hits, "misses": misses}

        return memoize, stats

    memoize_fn, stats_fn = make_memoizer()
    print("Q1 output:")
    print(memoize_fn.__closure__)
    print(stats_fn.__closure__)
    print([cell.cell_contents for cell in memoize_fn.__closure__])
    print([cell.cell_contents for cell in stats_fn.__closure__])


q1_demo()
print()


# ============================================================
# Question 2
# ============================================================

# Question Section:
# Predict the output:
# def make_pair():
#     value = [0]
#     def get(): return value[0]
#     def set_(x): value[0] = x
#     return get, set_
#
# get1, set1 = make_pair()
# get2, set2 = make_pair()
# set1(10)
# print(get1(), get2())
#
# Why does this work without nonlocal anywhere, even though set_ is clearly
# mutating something from the enclosing scope?

# Answer Section:
# This works because the code mutates the contents of the list object, not the
# variable `value` itself. The list is a mutable object, so `value[0] = x`
# changes the list in place. Each call to make_pair() creates a different list,
# so each pair's state is isolated. Output:
# 10 0

# Executable Independent Code Section:
def q2_demo():
    def make_pair():
        value = [0]

        def get():
            return value[0]

        def set_(x):
            value[0] = x

        return get, set_

    get1, set1 = make_pair()
    get2, set2 = make_pair()
    set1(10)
    print("Q2 output:")
    print(get1(), get2())


q2_demo()
print()


# ============================================================
# Question 3
# ============================================================

# Question Section:
# If you call make_counter() five times and never store four of the five returned
# increment functions anywhere, what happens to their count cells? Does Python's
# garbage collector need anything special to reclaim them?

# Answer Section:
# If the closure objects are no longer referenced, Python reclaims them automatically.
# No special manual cleanup is required. The count cells belong to those closure
# objects, and once the functions are unreachable, they are garbage-collected.

# Executable Independent Code Section:
def q3_demo():
    def make_counter():
        count = 0

        def increment():
            nonlocal count
            count += 1
            return count

        return increment

    c1 = make_counter()
    c2 = make_counter()
    c3 = make_counter()
    c4 = make_counter()
    c5 = make_counter()

    print("Q3 output:")
    print(c1(), c1(), c1())
    print("The unreferenced closures are eventually garbage-collected automatically.")


q3_demo()
print()


# ============================================================
# Question 4
# ============================================================

# Question Section:
# Why does Python require nonlocal (or the trick in question 2) for reassignment
# of an outer variable, but requires nothing special to merely read an outer
# variable? What does this reveal about how the compiler decides a name is
# "local" versus "free"?

# Answer Section:
# Python decides scope statically. If a name is assigned anywhere inside a function,
# the compiler treats it as a local variable for the entire function body. Reading
# without assignment means it is treated as a free variable from the enclosing scope.
# `nonlocal` tells Python to use the outer function variable instead of creating
# a new local binding.

# Executable Independent Code Section:
def q4_demo():
    x = 10

    def read_outer():
        print("outer x =", x)

    def rebind_enclosing():
        x = 10

        def inner():
            nonlocal x
            x += 1
            return x

        return inner

    print("Q4 output:")
    read_outer()
    print("inner returns:", rebind_enclosing()())

q4_demo()
print()


# ============================================================
# Question 5
# ============================================================

# Question Section:
# Given the loop-capture bug fix (lambda i=i: ...), would wrapping the loop body
# in a small helper function:
# def make_handler(i): return lambda: i
# and calling make_handler(i) inside the loop also fix the bug?
# Why does creating a new function call per iteration matter here?

# Answer Section:
# Yes. Each call to make_handler(i) creates a new function object and captures
# the current value of i. Because each closure is created in a separate function
# call, each one gets its own saved value. This prevents the classic late-binding
# bug where all handlers share the final loop variable.

# Executable Independent Code Section:
def q5_demo():
    def make_handler(i):
        return lambda: i

    handlers = []
    for i in range(3):
        handlers.append(make_handler(i))

    print("Q5 output:")
    for h in handlers:
        print(h())


q5_demo()
