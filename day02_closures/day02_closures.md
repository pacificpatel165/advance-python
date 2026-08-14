# Day 2 — Closures

*Advanced Python Learning Path | 2026-08-13*

*Builds on Day 1 (functions as first-class values, LEGB scope resolution).*

---

## 1. Concept Introduction

A **closure** is an inner function that "remembers" the variables from its enclosing (parent) function's scope, even after the parent function has finished running and returned. The inner function carries its own private snapshot of the environment it was created in, wherever it goes.

This is advanced/professional territory because it breaks the naive intuition that "a function's local variables disappear once the function returns." Closures show that Python's variable lifetime isn't tied to a call frame disappearing — it's tied to whether anything still *references* that variable. An inner function referencing an outer variable is exactly that kind of reference, and it keeps the variable alive.

**Problem this solves:** without closures, the only way to give a function some persistent, private configuration or state is a class with `__init__` and instance attributes — even when all you need is "one number this function remembers." Closures let you attach state to a function without the ceremony of a class, and they are the exact mechanism that makes decorators (tomorrow), callback factories, and memoization helpers work.

---

## 2. Build Intuition

Recall from Day 1: `make_multiplier` returned an inner function `multiplier` that used `factor` from the enclosing scope. That was already a closure — we just hadn't named it yet.

**Mental model:** think of a closure as a function bundled with a small backpack. The backpack contains references to the specific outer variables the function actually uses. When you call `make_multiplier(2)`, Python packs `factor = 2` into `multiplier`'s backpack before handing `multiplier` back to you. The backpack travels with the function forever, independent of whether `make_multiplier` itself is still "running."

Step by step:

**Step 1 — an inner function referencing an outer variable:**
```python
def make_greeter(greeting: str):
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"   # 'greeting' isn't local to greet
    return greet

hello = make_greeter("Hello")
print(hello("Prashant"))  # Hello, Prashant!
```
`make_greeter("Hello")` has already returned by the time `hello("Prashant")` runs. Yet `greeting` is still there. That's the closure at work.

**Step 2 — inspecting the backpack directly:**
```python
print(hello.__closure__)              # (<cell at 0x...: str object at 0x...>,)
print(hello.__closure__[0].cell_contents)  # 'Hello'
print(hello.__code__.co_freevars)     # ('greeting',)
```

**Step 3 — a closure with *mutable* remembered state (needs `nonlocal`):**
```python
def make_counter():
    count = 0
    def increment() -> int:
        nonlocal count      # without this, count += 1 would raise UnboundLocalError
        count += 1
        return count
    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

**Step 4 — independent closures don't share state:**
```python
counter_a = make_counter()
counter_b = make_counter()
print(counter_a())  # 1
print(counter_a())  # 2
print(counter_b())  # 1  -- counter_b has its own separate 'count' cell
```

> 📄 Runnable file: [`examples/step_by_step.py`](examples/step_by_step.py)

---

## 3. How Python Works Internally

- **Free variables vs. local variables.** When the compiler processes `increment`'s body, it sees `count` is *used* but never assigned as a plain local (thanks to `nonlocal`), so it classifies `count` as a **free variable** rather than a local. Free variables are stored differently from ordinary locals.

- **Cells.** For each free variable, Python allocates a small object called a **cell** (`cell` object, part of `types`). Both the enclosing function's local binding and the inner function's free-variable reference point at the *same cell*, not at the value directly. The cell itself holds the actual value and can be mutated in place. This indirection is exactly what lets `nonlocal count; count += 1` update a value that both `make_counter`'s (now-finished) frame and `increment` can see consistently.

- **`__closure__` and `co_freevars`.** A function object with free variables has a non-`None` `__closure__` attribute — a tuple of cell objects, one per free variable, in the order given by `func.__code__.co_freevars`. This is literally "the backpack" from the analogy — it is a real, inspectable tuple.

- **Why the enclosing frame's variable survives.** Normally, when a function returns, its stack frame is discarded and its local variables become garbage (their reference count drops to zero, CPython frees them immediately). But if an inner function holds a reference to a cell from that frame, the cell's reference count stays above zero, so the cell — and the value inside it — outlives the frame that created it. This is ordinary reference counting, not a special "closures" feature; closures work *because of* Python's general memory model, not despite it.

- **Late binding, again.** Because the inner function looks up the free variable through the cell at *call time*, not at definition time, if the enclosing variable changes after the closure is created but before it's called, the closure sees the new value. This is exactly the mechanism behind the classic loop-closure bug from Day 1 — now you know precisely why: all the lambdas in the loop share the *same* cell for `i`, and that cell holds whatever `i` was left at when the loop ended.

---

## 4. Practical Usage

**Where it's used:**
- **Decorators** (tomorrow's topic) are built entirely from closures — a decorator is a function that takes a function and returns a new function which closes over the original.
- **Callback/event-handler factories** — e.g., a GUI or web framework generating a handler pre-configured with a specific ID or context: `make_delete_handler(item_id)`.
- **Memoization/caching helpers** — a closure over a private cache dict, without exposing that dict as a public attribute.
- **Partial configuration** — functions that "bake in" some arguments and return a narrower function, similar in spirit to `functools.partial` but with custom logic.
- **Simple state machines / counters / rate limiters** — small pieces of private mutable state attached to a function, without needing a full class.

**Advantages:** encapsulation without a class — the enclosed state (like `count`) is genuinely private; nothing outside the closure can reach the cell directly. Less boilerplate than `__init__` + `self.count` for a single piece of state. Enables elegant factory functions that produce many independently configured functions.

**Trade-offs:** closures hide state in a way that's harder to inspect/debug than an object's `__dict__` — you need `__closure__` introspection or a debugger to see it. If a closure needs to track *several* pieces of related state, or needs multiple methods operating on that state, a class is clearer and more maintainable than a tangle of `nonlocal` variables. Closures over mutable objects (like a list you keep appending to) can also create subtle memory-retention issues if you're not intentional about their lifetime.

**When to prefer a simpler alternative:** if you only need to pass one fixed value into a function once, don't build a closure factory — pass an argument. If you need multiple related pieces of state and multiple operations on them, prefer a small class (a `dataclass` with methods) over a closure with three or four `nonlocal` variables — the class is more readable and testable.

---

## 5. Code Examples

### 5.1 Basic example
```python
def make_power(exponent: int):
    def power(base: float) -> float:
        return base ** exponent
    return power

square = make_power(2)
cube = make_power(3)
print(square(5))  # 25
print(cube(2))    # 8
```
`exponent` is captured once per call to `make_power`, so `square` and `cube` each carry their own independent value.

> 📄 Runnable file: [`examples/basic_power.py`](examples/basic_power.py)

### 5.2 Intermediate example
```python
from typing import Callable

def make_rate_limiter(max_calls: int) -> Callable[[], bool]:
    """Returns a function that reports True if a call is still allowed."""
    calls_made = 0

    def allow_call() -> bool:
        nonlocal calls_made
        if calls_made >= max_calls:
            return False
        calls_made += 1
        return True

    return allow_call

limiter = make_rate_limiter(3)
results = [limiter() for _ in range(5)]
print(results)  # [True, True, True, False, False]
```
`calls_made` is fully private to this particular `limiter` instance — no external code can reset or peek at it except through `allow_call` itself. This is real encapsulation, achieved without a class.

> 📄 Runnable file: [`examples/rate_limiter.py`](examples/rate_limiter.py)

### 5.3 Real-world/project-oriented example
```python
from __future__ import annotations
from typing import Callable
import time

Number = float

def make_memoizer() -> tuple[Callable, Callable[[Callable], Callable]]:
    """
    Returns a (stats, memoize) pair. `memoize` wraps any single-argument
    function with a private cache closure; `stats` reports hit/miss counts
    for whichever function was wrapped, without exposing the cache dict.
    """
    hits = 0
    misses = 0

    def memoize(func: Callable[[Number], Number]) -> Callable[[Number], Number]:
        cache: dict[Number, Number] = {}

        def wrapped(n: Number) -> Number:
            nonlocal hits, misses
            if n in cache:
                hits += 1
                return cache[n]
            misses += 1
            result = func(n)
            cache[n] = result
            return result

        return wrapped

    def stats() -> dict[str, int]:
        return {"hits": hits, "misses": misses}

    return stats, memoize


def slow_square(n: Number) -> Number:
    time.sleep(0.01)  # simulate expensive work
    return n * n


get_stats, memoize = make_memoizer()
fast_square = memoize(slow_square)

for value in [2, 3, 2, 4, 2, 3]:
    fast_square(value)

print(get_stats())  # {'hits': 3, 'misses': 3}
```
This mirrors real caching layers: `memoize` closes over a private `cache` dict per wrapped function, and `hits`/`misses` are closed over by *both* `memoize`'s inner function and the outer `stats` function — two different closures sharing the same cells, which is exactly how a decorator later exposes bookkeeping metadata (`wrapper.cache_info()` in `functools.lru_cache` works on this same principle).

> 📄 Runnable file: [`examples/memoizer.py`](examples/memoizer.py)

---

## 6. Project Application

- **Decorators (tomorrow):** every decorator you'll write is a closure — `def decorator(func): def wrapper(*a, **kw): ...; return wrapper; return decorator`. Understanding today's cell/free-variable mechanics is the direct prerequisite for understanding why decorators can add behavior around a function without modifying its source.
- **FastAPI / web frameworks:** dependency factories and route-specific configuration often use closures — e.g., a function `require_role(role: str)` that returns a dependency-check function closing over `role`, used as `Depends(require_role("admin"))`.
- **Background workers / task queues:** a worker might build a task function via a closure that bakes in a database connection or a specific queue name, so the dispatched callable doesn't need those passed explicitly each time.
- **Testing:** closures are common in test fixtures and fakes — a fake HTTP client factory `make_fake_client(responses: dict)` returns a `get(url)` closure that looks up canned responses, entirely in-memory, no class needed.
- **Configuration-driven CLIs:** a CLI command builder can produce closures pre-configured with parsed argument values, deferring execution until the command actually runs.

In a clean/modular architecture, closures typically live in **factory functions** at module or application-wiring level — anywhere you see `def make_X(...): def inner(...): ...; return inner`, that's a closure factory, usually sitting at the boundary where configuration turns into behavior.

---

## 7. Common Mistakes

**Mistake 1 — forgetting `nonlocal` when mutating an outer variable.**
```python
# BAD: raises UnboundLocalError
def make_counter():
    count = 0
    def increment():
        count += 1   # Python sees an assignment to `count` inside increment,
        return count # so it treats `count` as LOCAL to increment -- but it's
                      # read before being assigned locally -> error
    return increment

# BETTER
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
```
This is a compile-time scoping decision: if *any* assignment to a name exists anywhere in a function body, Python treats that name as local for the *entire* function body, even before the assignment line runs — hence the error on read.

**Mistake 2 — the classic loop-capture bug, revisited with full understanding.**
```python
# BAD: all closures share the same cell for `i`
handlers = []
for i in range(3):
    def handler():
        return i
    handlers.append(handler)
print([h() for h in handlers])  # [2, 2, 2]

# BETTER: force a new cell per iteration via a default argument
handlers = []
for i in range(3):
    def handler(i=i):
        return i
    handlers.append(handler)
print([h() for h in handlers])  # [0, 1, 2]
```

**Mistake 3 — closing over a mutable object you keep mutating elsewhere**, expecting the closure to have "snapshotted" it:
```python
config = {"debug": False}

def make_logger():
    def log(msg: str):
        if config["debug"]:
            print(f"[DEBUG] {msg}")
    return log

logger = make_logger()
config["debug"] = True   # logger sees this change -- config is captured by reference
logger("test")           # prints, which may surprise someone expecting a snapshot
```
Closures capture *references* to variables/cells, not frozen values — this is correct and useful for shared live config, but a mistake if you actually wanted an immutable snapshot at creation time (fix: capture a copy explicitly, e.g., `debug = config["debug"]` at closure-creation time).

**Mistake 4 — using a closure with three-plus `nonlocal` variables where a class would be clearer.** A closure that has grown `nonlocal a, b, c` plus several inner functions manipulating them is a sign the code wants to be a class — it's the same encapsulation, but classes make the state visible as named attributes and support multiple named methods without threading everything through one factory function.

> 📄 Runnable file: [`examples/common_mistakes.py`](examples/common_mistakes.py)

---

## 8. Compare With Alternatives

**Closure vs. class with instance attributes.** Both give you state bundled with behavior. A closure is leaner for a single function with a small amount of private state and one operation (e.g., a counter, a memoizer for one function). A class is better once you need multiple methods operating on shared state, need that state to be introspectable/testable via attributes, or need the object to participate in inheritance or a type hierarchy (e.g., implementing a Protocol/ABC).

**Closure vs. `functools.partial`.** `partial` pre-binds *arguments* to an existing function — it doesn't let you add new logic or private state, just fix some inputs. A closure can pre-bind values *and* introduce entirely new behavior/state around them. Use `partial` for simple argument-binding; use a closure (or decorator) when you need actual new logic wrapped around the captured values.

**Closure vs. global/module-level state.** A global variable is shared by everything that imports the module — no isolation, easy to accidentally corrupt from unrelated code. A closure's captured variable is private to that specific closure instance — two calls to the same factory function produce two independent, non-interfering states (see Step 4 in Section 2). Prefer closures (or classes) over module globals whenever you need more than one independent instance of the state.

---

## 9. Deep-Dive Questions

Attempt these before scrolling past them — no answers are given here.

1. In the `make_memoizer` example (5.3), `hits` and `misses` are free variables in *two different* inner functions (`wrapped` and `stats`), defined in two different `def` blocks. Are they sharing the same cell, or does each inner function get its own? How would you verify this using `__closure__`?
2. Predict the output:
   ```python
   def make_pair():
       value = [0]
       def get(): return value[0]
       def set_(x): value[0] = x
       return get, set_

   get1, set1 = make_pair()
   get2, set2 = make_pair()
   set1(10)
   print(get1(), get2())
   ```
   Why does this work *without* `nonlocal` anywhere, even though `set_` is clearly mutating something from the enclosing scope?
3. If you call `make_counter()` (from Section 2/7) five times and never store four of the five returned `increment` functions anywhere, what happens to their `count` cells? Does Python's garbage collector need anything special to reclaim them?
4. Why does Python require `nonlocal` (or the trick in question 2) for reassignment of an outer variable, but requires *nothing special* to merely *read* an outer variable? What does this reveal about how the compiler decides a name is "local" versus "free"?
5. Given the loop-capture bug fix (`lambda i=i: ...`), would wrapping the loop body in a small helper function `def make_handler(i): return lambda: i` and calling `make_handler(i)` inside the loop also fix the bug? Why does creating a new function call per iteration matter here?

---

## 10. Hands-On Exercise

Build this incrementally — don't skip to the hardest part.

**Part A (basic):** Write `make_running_average()` that returns a function `add(value: float) -> float`, where each call to `add` supplies a new number and returns the *running average* of all numbers supplied so far. Test: calling `add(10)`, `add(20)`, `add(30)` in sequence should return `10.0`, `15.0`, `20.0`.

**Part B (intermediate):** Write `make_event_bus()` that returns a `(subscribe, publish)` pair of closures sharing private state: `subscribe(handler)` registers a callback, and `publish(event)` calls every registered handler with `event`. No class, no global list — all state lives in cells shared between the two closures.

**Part C (project-style):** Write `make_config_gate(get_flag: Callable[[], bool])` that returns a decorator-like closure `guard(func)`, where `guard(func)` returns a new function that only calls `func(*args, **kwargs)` if `get_flag()` currently returns `True`, otherwise returns `None` and prints `"blocked: feature disabled"`. This is a preview of tomorrow's decorators, built with only today's tools — notice that `guard` closes over `get_flag`, and the function it returns closes over `func`, two nested layers of closures.

Do not look up a solution before attempting all three parts yourself.

> 📄 Starter file (TODOs, no solution): [`exercises/exercise_day02.py`](exercises/exercise_day02.py)

---

## 11. Advanced Challenge

Build a small **debounced dispatcher** that combines closures, mutable captured state, and Day 1's first-class functions:

```python
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
    behavior is deterministic and testable -- reason about why this
    injection matters before writing the test.
    """
    ...
```

Requirements to reason through before coding:
- You need at least two pieces of private state per wrapped function: the last call timestamp and the last result — both must be `nonlocal` inside `guarded`.
- Because `clock` is a parameter of `make_debouncer` (not called directly as `time.time()`), you can pass a fake, controllable clock in tests — e.g., a closure of your own, `make_fake_clock()`, returning `(advance, clock)` where `advance(seconds)` moves the fake clock forward.
- Verify: calling the guarded function rapidly should only actually invoke the underlying function once per `min_interval_seconds` window; write a test using your fake clock to prove it deterministically, without any real `time.sleep`.

This mirrors real debouncing/throttling logic in UI event handlers, rate-limited API clients, and monitoring/alerting systems — all built from nothing more than "a closure remembering some private state between calls."

> 📄 Starter file (TODOs, no solution): [`challenge/debounced_dispatcher.py`](challenge/debounced_dispatcher.py)

---

## 12. Professional Perspective

**What an experienced Python developer should understand:** a closure is not a syntax trick, it is the direct, visible consequence of Python's reference-based variable model meeting nested function scopes — a free variable survives exactly as long as something still references its cell, no more, no less. Once that clicks, closures stop looking like magic and start looking like the *lightest possible* way to attach private, persistent state to a function. An experienced developer reaches for a closure when the state is small and single-purpose, and reaches for a class the moment that state grows multiple related pieces or multiple operations — recognizing that boundary is itself the professional judgment call, not the ability to write `nonlocal`.

---

## Recap

- A closure is an inner function that retains references to free variables from an enclosing scope, even after that scope's function has returned.
- Internally, each free variable lives in a shared **cell** object; the inner function's `__closure__` tuple holds references to these cells, which is why the captured state outlives the enclosing call frame — ordinary reference counting keeps the cell alive.
- Reading an outer variable needs nothing special; *reassigning* one requires `nonlocal`, because the compiler decides "local vs. free" for an entire function body based on whether any assignment to that name exists anywhere in it.
- Closures capture references, not snapshots — mutating the outer variable after closure creation is visible inside the closure, which is a feature when intentional and a bug when assumed to be a snapshot.
- Closures are the direct mechanism behind decorators, tomorrow's topic: a decorator is simply a closure over the original function.

**Next up (Day 3): Decorators** — how to use closures to wrap a function with additional behavior (logging, timing, retries, access control) without modifying its source, and how `functools.wraps` preserves the original function's identity through the wrap.
