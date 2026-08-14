# Day 3 — Decorators

*Advanced Python Learning Path | 2026-08-13*

*Builds on Day 1 (functions as first-class values) and Day 2 (closures, cells, free variables).*

---

## 1. Concept Introduction

A **decorator** is a function that takes another function (or class) as input and returns a new callable that wraps the original with extra behavior — logging, timing, retries, access control, caching — without touching the original function's source code. `@decorator` above a `def` is just syntax sugar for `func = decorator(func)`.

This is advanced/professional territory because a decorator is not a new language feature — it is Day 2's closures applied to a specific, extremely common problem: "I need to run some code before and/or after every call to this function, for many different functions, without duplicating that code inside each one." Recognizing a decorator as "just a closure factory with a name and `@` syntax" is what separates using decorators from truly understanding them.

**Problem this solves:** without decorators, cross-cutting behavior (logging, timing, auth checks, retries, caching) either gets copy-pasted into every function that needs it, or the caller has to remember to manually wrap each call site (`log_call(do_work)()`). Neither scales. Decorators let you attach that behavior declaratively, once, at the definition site, and have it apply uniformly and automatically every time the function is called.

---

## 2. Build Intuition

**Mental model:** a decorator is a gift-wrapping machine. You feed it a function; it hands back a *different* function — one that still does the original's job, but is now wrapped in extra paper (behavior) on the way in and/or out. Callers can't tell the difference except that the extra behavior now always happens.

Step by step:

**Step 1 — manually wrapping a function (no `@` yet):**
```python
def shout(text: str) -> str:
    return text.upper()

def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__} with {args}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

shout = add_logging(shout)   # manual decoration
shout("hello")
# calling shout with ('hello',)
# shout returned 'HELLO'
```
`add_logging` is a Day-2 closure factory: `wrapper` closes over `func`. Nothing new yet.

**Step 2 — the same thing with `@` syntax:**
```python
@add_logging
def shout(text: str) -> str:
    return text.upper()
```
This line is executed by Python as exactly `shout = add_logging(shout)`, immediately, at module-load time — not at call time. The `@` is purely sugar for "reassign this name to the decorator's return value."

**Step 3 — preserving identity with `functools.wraps`:**
```python
from functools import wraps

def add_logging(func):
    @wraps(func)          # copies __name__, __doc__, __wrapped__, etc. onto wrapper
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__} with {args}")
        return func(*args, **kwargs)
    return wrapper

@add_logging
def shout(text: str) -> str:
    """Uppercase the given text."""
    return text.upper()

print(shout.__name__)  # 'shout', not 'wrapper'
print(shout.__doc__)   # 'Uppercase the given text.'
```

**Step 4 — a decorator *factory* (a decorator that takes arguments):**
```python
def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def ping():
    print("ping")

ping()  # prints "ping" three times
```
This is three nested layers of closures: `repeat(times=3)` returns `decorator`, which closes over `times`; `decorator(ping)` returns `wrapper`, which closes over `func` *and* (transitively, through `decorator`'s cell) `times`. `@repeat(times=3)` is sugar for `ping = repeat(times=3)(ping)` — the extra parentheses are what make it a factory instead of a plain decorator.

> 📄 Runnable file: [`examples/step_by_step.py`](examples/step_by_step.py)

---

## 3. How Python Works Internally

- **`@decorator` is not special syntax at the bytecode level for "decoration."** It compiles to a function call followed by a name rebinding: `def f(): ...` followed by `f = decorator(f)`. The `@` line simply tells the compiler to emit that call immediately after building the function object, before binding it to the name `f` in the enclosing namespace.

- **Decoration happens at *import/definition* time, once — not at call time.** This is a common source of confusion: people expect decorator setup code (e.g., print statements inside `decorator` but outside `wrapper`) to run on every call. It actually runs exactly once, when the module is loaded and the `def` statement executes. Only code inside `wrapper` runs on every call.

- **The returned object is a completely different function object.** After `func = decorator(func)`, the name `func` no longer refers to the original function object at all — it refers to `wrapper`. The original function object still exists (kept alive by `wrapper`'s closure cell referencing it, per Day 2's reference-counting rules) but is no longer reachable by its original name unless you kept a separate reference.

- **`functools.wraps` is itself a decorator (built on `functools.update_wrapper`).** It copies `__name__`, `__doc__`, `__module__`, `__dict__`, and `__qualname__` from the original function onto the wrapper, and — critically — sets `wrapper.__wrapped__ = func`. That `__wrapped__` attribute is what lets introspection tools (`inspect.signature`, debuggers, `help()`) see through the wrapper to the original function's real signature. Without it, `wrapper`'s signature is just `(*args, **kwargs)`, which is a real loss of information for anyone (including type checkers and IDEs) inspecting the decorated function.

- **Stacking decorators applies bottom-up, calls top-down.** 
  ```python
  @a
  @b
  def f(): ...
  ```
  is `f = a(b(f))`. So `b` wraps the original `f` first (closest to the `def`), then `a` wraps *that*. When you call `f()`, `a`'s wrapper code runs first (outermost), then it calls into `b`'s wrapper, which finally calls the real `f`. Order matters and is a frequent source of subtle bugs (e.g., a `@cache` decorator placed outside a `@log_calls` decorator will suppress logging on cache hits, since the inner wrapper never runs).

---

## 4. Practical Usage

**Where it's used:**
- **Web frameworks** (FastAPI, Flask, Django): route registration (`@app.get("/users")`), authentication/authorization guards, request validation.
- **Caching**: `functools.lru_cache`/`cache` are decorators; custom decorators wrap expensive functions with a private cache (Day 2's memoizer, now with `@` syntax).
- **Retries and resilience**: `@retry(max_attempts=3)` around flaky network calls.
- **Timing/profiling**: `@timed` around functions you want to benchmark without littering `time.time()` calls everywhere.
- **Access control**: `@require_role("admin")` around sensitive functions or endpoints.
- **Testing**: `pytest` fixtures and markers (`@pytest.fixture`, `@pytest.mark.parametrize`) are decorators; `unittest.mock.patch` is commonly used as a decorator.
- **Registration patterns**: `@app.command()` in CLI frameworks like Typer/Click, `@dataclass` itself is a class decorator.

**Advantages:** behavior is declared once, next to the function it affects, and applies automatically and consistently every time the function is called; keeps the function's own body focused on its actual logic (separation of concerns); composable — multiple decorators stack.

**Trade-offs:** adds a layer of indirection that can make stack traces and debugging harder (mitigated by `functools.wraps`, but not eliminated — you still have an extra call frame per decorator); decorator order matters and is easy to get wrong; decorators that swallow exceptions or silently alter return values can hide bugs; heavily decorated code can be harder for newcomers to trace mentally ("what does this function *actually* do") compared to explicit code.

**When to prefer a simpler alternative:** if the "extra behavior" is needed at exactly one call site, just write it inline — a decorator adds indirection that isn't earning its keep for a one-off. If the wrapping logic needs significant per-call context that's awkward to pass through `*args, **kwargs`, an explicit helper function or a class-based approach may be clearer than a decorator.

---

## 5. Code Examples

### 5.1 Basic example
```python
from functools import wraps
import time

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper

@timed
def slow_add(a: int, b: int) -> int:
    time.sleep(0.05)
    return a + b

print(slow_add(2, 3))
```
`wrapper` accepts `*args, **kwargs` so `timed` works on *any* function signature, not just one specific one — this generality is the whole point of writing the decorator once and reusing it everywhere.

> 📄 Runnable file: [`examples/basic_timed.py`](examples/basic_timed.py)

### 5.2 Intermediate example
```python
from functools import wraps
from typing import Callable, TypeVar
import time

F = TypeVar("F", bound=Callable[..., object])

def retry(max_attempts: int, delay_seconds: float = 0.0) -> Callable[[F], F]:
    """Decorator factory: retries a function on exception, up to max_attempts."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    print(f"attempt {attempt} failed: {exc!r}")
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)
            assert last_exc is not None
            raise last_exc
        return wrapper  # type: ignore[return-value]
    return decorator

_flaky_calls = 0

@retry(max_attempts=3)
def flaky() -> str:
    global _flaky_calls
    _flaky_calls += 1
    if _flaky_calls < 3:
        raise ConnectionError("simulated network failure")
    return "success"

print(flaky())  # fails twice, then "success"
```
`retry` is a **decorator factory**: calling `retry(max_attempts=3)` returns the actual decorator, which is what gets applied to `flaky`. Catching `Exception`, re-raising the *last* exception rather than swallowing it, and using `TypeVar` to preserve the wrapped function's type for static analysis are all deliberate professional choices — a decorator that swallows every exception silently is a common and dangerous anti-pattern (see Section 7).

> 📄 Runnable file: [`examples/retry_decorator.py`](examples/retry_decorator.py)

### 5.3 Real-world/project-oriented example
```python
from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar
import logging
import time

logger = logging.getLogger("api")
F = TypeVar("F", bound=Callable[..., object])


class AuthorizationError(Exception):
    """Raised when the current caller lacks the required role."""


def require_role(role: str) -> Callable[[F], F]:
    """
    Decorator factory used on service-layer functions. Expects the wrapped
    function's first positional argument to be a `context` object exposing
    `context.user_role`. This mirrors how FastAPI dependencies or Django
    view decorators check permissions before running the real handler.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(context, *args, **kwargs):
            if context.user_role != role:
                logger.warning(
                    "authorization denied: user_role=%r required=%r func=%s",
                    context.user_role, role, func.__name__,
                )
                raise AuthorizationError(f"requires role '{role}'")
            return func(context, *args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator


def log_and_time(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info("start %s", func.__name__)
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception("error in %s", func.__name__)
            raise
        else:
            elapsed = time.perf_counter() - start
            logger.info("done %s in %.4fs", func.__name__, elapsed)
            return result
    return wrapper  # type: ignore[return-value]


class RequestContext:
    def __init__(self, user_role: str) -> None:
        self.user_role = user_role


@log_and_time
@require_role("admin")
def delete_user(context: RequestContext, user_id: int) -> str:
    return f"user {user_id} deleted"


try:
    delete_user(RequestContext(user_role="viewer"), 42)
except AuthorizationError as exc:
    print(f"blocked: {exc}")

print(delete_user(RequestContext(user_role="admin"), 42))
```
Note the **stacking order**: `@log_and_time` is outermost, `@require_role("admin")` is innermost, i.e. `delete_user = log_and_time(require_role("admin")(delete_user))`. This means every call — allowed or denied — gets logged and timed, including the `AuthorizationError` path (thanks to the `except`/`logger.exception`/`raise` pattern re-raising rather than swallowing). If the order were reversed, a denied call would never reach `require_role`'s check consistently with logging wrapped around it the same way — order changes *what gets observed*, not just performance.

> 📄 Runnable file: [`examples/service_layer_guards.py`](examples/service_layer_guards.py)

---

## 6. Project Application

- **FastAPI / REST APIs:** route decorators (`@app.get(...)`) register handlers with the framework's routing table; custom decorators or dependencies enforce auth, rate limiting, and request logging around handler functions, typically in a `middleware/` or `decorators/` module shared across routers.
- **Background workers:** task decorators (`@app.task` in Celery-style systems) register a plain function as a dispatchable unit of work, and can layer retry/backoff behavior identical in spirit to Section 5.2's `retry`.
- **Database applications:** `@transactional` decorators wrap a function's body in a DB transaction (begin/commit/rollback), so the function itself only contains business logic — the transaction boundary is cross-cutting concern handled by the decorator.
- **CLI applications:** Click/Typer use decorators (`@click.command()`, `@click.option(...)`) to turn plain functions into CLI commands with argument parsing attached.
- **Testing:** `@pytest.fixture`, `@pytest.mark.parametrize`, and `@mock.patch` are all decorators that inject dependencies or vary test inputs without changing the test function's body.
- **Clean/modular architecture:** cross-cutting decorators (logging, auth, caching, retry) typically live in a shared `decorators.py` or `infrastructure/` layer, kept separate from business-logic modules — the business logic stays decorator-free and testable in isolation; decorators are applied at the boundary (e.g., the API/route layer) where cross-cutting concerns belong.

---

## 7. Common Mistakes

**Mistake 1 — forgetting `functools.wraps`.**
```python
# BAD
def log_calls(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@log_calls
def compute_total(items): ...

print(compute_total.__name__)  # 'wrapper' -- breaks introspection, docs, debuggers

# BETTER
from functools import wraps
def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

**Mistake 2 — a decorator that swallows exceptions silently.**
```python
# BAD: hides real bugs, callers get None with no explanation
def safe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None
    return wrapper

# BETTER: log and re-raise, or handle only the specific exceptions you expect
def safe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError):
            logger.exception("expected failure in %s", func.__name__)
            return None
        # anything else propagates -- unexpected bugs stay visible
    return wrapper
```

**Mistake 3 — mutable default state shared across all calls when it shouldn't be.**
```python
# BAD: cache is a single dict shared by EVERY function decorated with @memoize,
# keyed only by args -- collisions possible if reused carelessly, and there's
# no way to reset one function's cache independently
_shared_cache = {}
def memoize(func):
    @wraps(func)
    def wrapper(*args):
        if args not in _shared_cache:
            _shared_cache[args] = func(*args)
        return _shared_cache[args]
    return wrapper

# BETTER: one private cache per decorated function (Day 2's closure-per-call lesson)
def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper
```

**Mistake 4 — decorating a function with the wrong decorator order, or applying a stateful decorator (like caching) outside a decorator whose side effects should run on every call** (see Section 3's `@cache` + `@log_calls` ordering issue) — always ask "which decorator should see every call, and which one should short-circuit the rest?" before choosing stacking order.

**Mistake 5 — using a decorator when a plain higher-order function call would be clearer**, e.g. permanently decorating a function used in exactly one place with `@retry(...)` when `retry(my_func)(...)` called explicitly at the one call site is just as correct and doesn't imply "this always retries everywhere," which is misleading if that's not actually true project-wide.

> 📄 Runnable file: [`examples/common_mistakes.py`](examples/common_mistakes.py)

---

## 8. Compare With Alternatives

**Decorator vs. plain higher-order function call.** `@decorator` above a `def` permanently rebinds the function's name to the wrapped version everywhere it's imported. Calling `decorator(func)(...)` explicitly at one call site wraps behavior only for that one use. Prefer `@` when the behavior should apply to *every* call to that function, everywhere; prefer an explicit call when only one call site needs the wrapping.

**Decorator vs. subclassing/inheritance for adding behavior.** A decorator adds behavior around a *function call*; inheritance adds/overrides behavior on a *class's methods*. For simple "run code before/after a callable," a decorator is far lighter weight than creating a subclass. For genuinely swappable *strategies* with multiple related behaviors and shared state, a class hierarchy (or composition, see Day-1-adjacent higher-order functions) is usually clearer.

**Function decorator vs. class decorator.** Everything above decorates functions; Python also allows `@decorator` on a class (`class C: ...` → `C = decorator(C)`), commonly used to add methods or validate structure (`@dataclass` is the canonical example, covered later in this path). Use a class decorator when you're augmenting a class's structure/behavior wholesale; use a function decorator when wrapping individual callables.

**`functools.lru_cache`/`cache` vs. a hand-written memoizing decorator.** Prefer the standard-library version whenever plain positional/keyword-hashable-argument caching is enough — it's tested, thread-considerations are documented, and it ships `cache_info()`/`cache_clear()` for free. Write your own only when you need custom cache keys, expiry, or per-argument-type logic the stdlib version doesn't support.

---

## 9. Deep-Dive Questions

Attempt these before scrolling past them — no answers are given here.

1. Given
   ```python
   @a
   @b
   @c
   def f(): ...
   ```
   write out the exact equivalent assignment expression using nested calls. If `a`, `b`, and `c` each print their name when their *outer* decorator function runs (not the inner wrapper), what order do those prints appear in when the module is loaded — before `f` is ever called?
2. Predict what happens (and why) if you decorate a function with a `retry`-style decorator (Section 5.2) that itself has a bug causing it to swallow the *last* exception instead of re-raising it after all attempts are exhausted. What would calling code observe, and why is this more dangerous than the exception simply propagating?
3. If a decorator's `wrapper` function does **not** accept `**kwargs`, but only `*args`, what specific category of bugs will show up later, and for whom (the decorator's author, or every future caller of the decorated function)?
4. `functools.wraps(func)` sets `wrapper.__wrapped__ = func`. Given that, how would you write a small utility function `unwrap_all(f)` that follows `__wrapped__` chains to find the original, undecorated function at the bottom of an arbitrary stack of decorators?
5. Why does a caching decorator (like `lru_cache`) placed as the *outermost* decorator in a stack risk suppressing the effects of an *inner* logging or authorization decorator on cache hits? Concretely, what would a user see (or not see) in the logs on the second call with identical arguments?

---

## 10. Hands-On Exercise

Build this incrementally — don't skip to the hardest part.

**Part A (basic):** Write a decorator `@log_arguments` that prints the decorated function's name, its positional args, and its keyword args every time it's called, then calls through to the original function and returns its result unchanged. Use `functools.wraps`.

**Part B (intermediate):** Write a decorator factory `@validate_positive(*param_names: str)` that, given the names of parameters that must be positive numbers, raises `ValueError` *before* calling the wrapped function if any named argument (found via `inspect.signature(func).bind(...)`) is `<= 0`. Test it on a function like `def charge_card(amount: float, tax: float) -> float: ...`.

**Part C (project-style):** Write a decorator `@cache_with_ttl(seconds: float, clock: Callable[[], float])` that memoizes a single-argument function's results, but treats a cached entry as expired (and recomputes) once `seconds` have passed since it was stored, using the injected `clock` rather than `time.time()` directly — exactly like Day 2's debouncer, `clock` injection is what makes this deterministically testable. Store `(value, stored_at)` per cache key.

Do not look up a solution before attempting all three parts yourself.

> 📄 Starter file (TODOs, no solution): [`exercises/exercise_day03.py`](exercises/exercise_day03.py)

---

## 11. Advanced Challenge

Combine today's decorators with Day 2's closures and Day 1's higher-order functions to build a **composable middleware pipeline**:

```python
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])

def compose_decorators(*decorators: Callable[[F], F]) -> Callable[[F], F]:
    """
    Returns a single decorator that applies the given decorators, in the
    order listed (leftmost decorator ends up OUTERMOST, i.e. it runs first
    on every call), equivalent to stacking them individually with @.

    compose_decorators(log_and_time, require_role("admin"))
    applied to a function should behave identically to:

        @log_and_time
        @require_role("admin")
        def f(...): ...
    """
    ...
```

Requirements to reason through before coding:
- You must apply the decorators in the correct order so that the *first* decorator in `compose_decorators(...)`'s argument list ends up outermost (runs first, on every call) — get the fold direction wrong and your composed pipeline will behave backwards from what its argument order suggests.
- Verify correctness by composing `log_and_time` and `require_role("admin")` from Section 5.3 both manually (via stacked `@`) and via `compose_decorators`, on two separate copies of the same underlying function, and asserting both produce identical behavior (same exceptions raised, same log order) for both an authorized and an unauthorized call.
- Bonus: make `compose_decorators` preserve the wrapped function's identity (`__name__`, `__doc__`) all the way through, even though it's composing an arbitrary number of decorators, each of which may or may not itself use `functools.wraps` correctly.

This mirrors real middleware/pipeline systems (web framework middleware stacks, ML preprocessing pipelines, ETL step chains) where the ability to compose a list of cross-cutting behaviors programmatically — rather than hand-writing `@a @b @c` every time — becomes valuable once the same combination is reused across many functions.

> 📄 Starter file (TODOs, no solution): [`challenge/middleware_pipeline.py`](challenge/middleware_pipeline.py)

---

## 12. Professional Perspective

**What an experienced Python developer should understand:** a decorator is nothing more than "a closure factory applied at definition time via `@` sugar" — there is no additional magic once Day 2's cell/closure model is solid. What makes decorators a professional-grade tool is not the syntax but the discipline around using them: always preserve identity with `functools.wraps`, always be deliberate about exception handling (never swallow silently), always reason explicitly about stacking order because it changes *which decorator sees which calls and failures*, and always ask whether the cross-cutting behavior actually needs to apply everywhere a function is used, or just at one call site. The experienced developer's instinct is to reach for a decorator exactly when behavior is genuinely cross-cutting and reusable — and to resist the temptation to decorate for its own sake, since every decorator is one more indirection a future reader has to mentally unwind to understand what a function really does.

---

## Recap

- A decorator is a function that takes a callable and returns a new callable wrapping it; `@decorator` above `def f` is sugar for `f = decorator(f)`, executed once at definition time, not per call.
- Decorators are Day 2's closures applied to the specific job of adding cross-cutting behavior (logging, timing, retries, auth, caching) without modifying the original function's source.
- `functools.wraps` copies the original function's metadata (`__name__`, `__doc__`, `__wrapped__`) onto the wrapper — skipping it silently breaks introspection, debugging, and documentation tools.
- A decorator *factory* (a decorator that itself takes arguments, e.g. `@retry(max_attempts=3)`) is one extra layer of nested closures: the factory returns the decorator, which returns the wrapper.
- Stacking order matters: `@a @b def f` is `a(b(f))`, so `a` is outermost and runs first on every call — this determines which decorator's side effects (logging, caching, auth checks) actually observe which calls.

**Next up (Day 4): Functional Programming Toolkit** — `functools.partial`, `functools.reduce`, `functools.singledispatch`, `itertools`, and the `operator` module, extending Day 1's higher-order functions into the standard library's dedicated functional-programming tools.
