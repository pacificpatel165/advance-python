"""
Day 4 -- Functional Programming Toolkit: advanced challenge (Section 11 of the lesson).

Build a composable data-pipeline runner that combines:
  - functools.reduce (to thread a value through a list of named steps)
  - functools.partial (where useful for pre-configuring steps)
  - a Day-3-style timing decorator (wrapping each step)
  - Day-2-style closures (the decorator itself, and the accumulator)

Do not look up a solution first.
"""
from __future__ import annotations

from functools import reduce, wraps
from time import perf_counter
from typing import Any, Callable, NamedTuple

Step = Callable[[Any], Any]


class StepTiming(NamedTuple):
    name: str
    seconds: float


class PipelineResult(NamedTuple):
    value: Any
    timings: list[StepTiming]


def timed_step(name: str, step: Step) -> Callable[[Any], tuple[Any, StepTiming]]:
    """
    TODO: return a callable that, given an input value, runs `step(value)`,
    measures elapsed wall-clock time with time.perf_counter(), and returns
    (result, StepTiming(name, elapsed_seconds)).

    Use @wraps appropriately if you introduce an inner wrapper function.
    """
    raise NotImplementedError


def compose_pipeline(named_steps: list[tuple[str, Step]]) -> Callable[[Any], PipelineResult]:
    """
    TODO: given a list of (name, step) pairs, return a single callable
    `run(initial_value) -> PipelineResult` that:
      1. Threads `initial_value` through every step in order (each step's
         output becomes the next step's input), using functools.reduce.
      2. Wraps each step with `timed_step` so you can record a StepTiming
         for every stage.
      3. Returns a PipelineResult with the final value and the full list
         of per-step timings, in order.

    Hint: reduce's accumulator can be a small tuple/object that carries
    both "the current value" and "the timings collected so far" -- you are
    not limited to folding a single scalar.
    """
    raise NotImplementedError


if __name__ == "__main__":
    def parse(raw: str) -> list[int]:
        return [int(x) for x in raw.split(",")]

    def normalize(values: list[int]) -> list[int]:
        total = sum(values) or 1
        return [round(v * 100 / total) for v in values]

    def to_summary(values: list[int]) -> str:
        return ", ".join(f"{v}%" for v in values)

    pipeline = compose_pipeline(
        [
            ("parse", parse),
            ("normalize", normalize),
            ("summarize", to_summary),
        ]
    )

    result = pipeline("10,20,30,40")
    print("final value:", result.value)
    for timing in result.timings:
        print(f"  {timing.name}: {timing.seconds:.6f}s")

    assert result.value == "10%, 20%, 30%, 40%"
    assert [t.name for t in result.timings] == ["parse", "normalize", "summarize"]
    print("All checks passed.")
