# Advanced Python Learning — Progress Tracker

Maintained automatically by the daily "advance-python-learning" scheduled task.
Do not delete — future lessons read this file to determine the next topic and avoid repetition.

## Folder Convention (starting Day 1)

Each day gets its own folder: `dayNN_topic_slug/`

```
dayNN_topic_slug/
  dayNN_topic_slug.md      <- full 13-section lesson (named after the folder, not "lesson.md" -- greppable)
  examples/                 <- runnable example .py files referenced from the lesson md
  exercises/                <- hands-on exercise starter file (TODOs, no solution)
  challenge/                <- advanced challenge starter file (TODOs, no solution)
```

Future daily runs should follow this structure rather than a single flat .md file.

## Path (in order)

Items marked **NEW** were added to fill gaps in the original list — each is inserted where it logically builds on the topic before it.

1. Advanced Functions (first-class functions, higher-order functions) — **DONE (2026-08-12)**
2. Closures
3. Decorators
4. Functional Programming Toolkit (`functools.partial`/`reduce`/`singledispatch`, `itertools`, `operator`) — **NEW**, extends Day 1's higher-order functions into the stdlib's functional tools
5. Iterators and Generators
6. Advanced Generator Patterns (`yield from`, `send`/`throw`/`close`, generator-based coroutines) — **NEW**, deepens generators before context managers/asyncio need them
7. Context Managers
8. Descriptors
9. Properties
10. `__slots__` and Memory-Efficient Objects — **NEW**, natural extension of properties/descriptors, sets up the later Memory day
11. Dataclasses
12. Enums and Structured Constants — **NEW**, common data-modeling companion to dataclasses
13. Abstract Base Classes
14. Protocols and Structural Typing
15. Type Hints and Generics
16. `__dunder__` Methods / Python Object Model
17. Metaclasses — **NEW**, the natural next step after the object model, before diving into memory
18. Memory and References
19. Weak References & Garbage Collection Internals — **NEW**, extends Memory and References
20. Exceptions and Custom Exception Design
21. Structural Pattern Matching (`match`/`case`) — **NEW**, modern control-flow tool often paired with custom exceptions/data classes
22. Logging
23. Observability Basics (metrics & tracing beyond logs) — **NEW**, extends Logging toward production monitoring
24. Testing and Mocking
25. Property-Based & Advanced Test Design (e.g. Hypothesis-style testing) — **NEW**, extends Testing and Mocking
26. Dependency Injection
27. Packaging
28. Configuration & Environment Management (settings, env vars, 12-factor-style config) — **NEW**, pairs with Packaging for shippable apps
29. Concurrency Overview
30. Threading
31. Multiprocessing
32. AsyncIO
33. Advanced AsyncIO (async generators, async context managers, `contextvars`) — **NEW**, deepens AsyncIO before Performance
34. Performance Optimization
35. Profiling
36. Caching Strategies (memoization, `lru_cache`, external caches) — **NEW**, extends Performance/Profiling
37. Advanced Standard Library
38. Serialization & Data Interchange (`json`, `pickle`, dataclass (de)serialization) — **NEW**, extends Advanced Standard Library
39. Design Patterns in Python
40. Clean Architecture
41. Pythonic Design
42. Metaprogramming (dynamic class creation, `exec`/`eval`, AST basics)
43. Advanced Typing (deep dive — variance, `TypedDict`, `overload`, `Protocol` composition)
44. Static Analysis & Type-Checking Tooling (mypy/pyright, linters) — **NEW**, extends Advanced Typing into daily workflow
45. CLI Application Design (argparse/click/typer patterns) — **NEW**, a common real-world Python deliverable not otherwise covered
46. Security Fundamentals for Python Applications (secrets, hashing, input validation, dependency risk) — **NEW**, essential before "production-oriented" close-out
47. Production-Oriented Python Practices

## Log

| Day | Date | Topic | Folder |
|---|---|---|---|
| 1 | 2026-08-12 | Advanced Functions (first-class & higher-order functions) | day01_advanced_functions/day01_advanced_functions.md |

## Next Scheduled Topic

**Day 2: Closures** — builds directly on Day 1 (functions as returned objects); explain how inner functions retain access to enclosing-scope variables, `nonlocal`, and how this sets up decorators for Day 3.
