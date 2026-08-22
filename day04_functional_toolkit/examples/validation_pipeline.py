"""
Day 4 -- Functional Programming Toolkit: intermediate example (Section 5.2 of the lesson).
Run directly: python validation_pipeline.py

WHAT THIS FILE DEMONSTRATES
----------------------------
A common real-world shape: "run N independent checks against one value, then
tell me whether ALL of them passed and collect EVERY failure message" (not
just the first one). This is the shape behind form validation, config
validation, and pre-flight checks before an API call or DB write.

The naive way to write this is a hand-rolled accumulator loop:

    is_valid = True
    errors = []
    for validator in validators:
        result = validator(value)
        if not result.is_valid:
            is_valid = False
            errors.extend(result.errors)

That works, but it's mutable, imperative, and re-derives the exact shape
that functools.reduce exists to express directly: "combine a sequence of
things into one thing, using a rule for combining two at a time." Below,
the same logic is built out of small, independently testable pieces and
then folded together -- which is the actual point of this exercise, not
just "here is how reduce works."
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Callable


@dataclass(frozen=True)
class ValidationResult:
    """
    Immutable (frozen=True) on purpose: a ValidationResult represents a fact
    about one already-evaluated check ("this input passed/failed, here's
    why"). Nothing about that fact should change after the fact is created --
    if it did, a `combine()` call further down the pipeline could end up
    silently mutating a result another part of the code still holds a
    reference to. Freezing it makes ValidationResult behave like a value,
    not an object with a lifecycle, which is exactly what you want for
    something that only ever gets *combined*, never *edited*.

    `errors` is a tuple, not a list, for the same reason: tuples are
    immutable, so two ValidationResults can safely share/reuse each other's
    `errors` data without either one being able to corrupt the other.
    """

    is_valid: bool
    errors: tuple[str, ...] = ()


def combine(a: ValidationResult, b: ValidationResult) -> ValidationResult:
    """
    This is the "binary function" that functools.reduce needs: given two
    ValidationResults, produce one ValidationResult that represents both of
    them together. This is the ONLY piece of logic that knows how two
    results merge -- every validator function below stays completely
    ignorant of the fact that it's going to be combined with others. That
    separation (checks don't know about combining; combining doesn't know
    about checks) is what makes each piece independently testable and
    reusable outside this specific pipeline.

    `a.is_valid and b.is_valid`: the whole pipeline is only valid if EVERY
    step is valid -- a single failure anywhere must fail the combined
    result. `a.errors + b.errors`: tuple concatenation, so no error message
    from either side is ever dropped, which is the entire reason this
    example doesn't just do `any()`/`all()` -- those would tell you *that*
    something failed, not *what* failed.
    """
    return ValidationResult(
        is_valid=a.is_valid and b.is_valid,
        errors=a.errors + b.errors,
    )


def not_empty(value: str) -> ValidationResult:
    """
    A validator's contract, by design, is deliberately narrow:
    `str -> ValidationResult`. It takes the value being checked and returns
    a self-contained verdict -- it does NOT raise, print, log, or know
    anything about other validators. That narrow, side-effect-free contract
    is exactly what lets `run_validators` below treat every validator
    interchangeably, and it's what functional-style code is actually
    buying you: predictable, composable units, not cleverness for its own
    sake.
    """
    stripped = value.strip()
    return ValidationResult(bool(stripped), () if stripped else ("must not be empty",))


def max_length(limit: int) -> Callable[[str], ValidationResult]:
    """
    This is a closure FACTORY (Day 2), included deliberately to show that
    Day 4's functional toolkit does not replace closures -- it sits on top
    of them. `not_empty` above needs no configuration, so it's a plain
    function. `max_length` needs a parameter (`limit`) that isn't part of
    the `str -> ValidationResult` validator contract, so it can't just take
    `limit` as a second argument -- `run_validators` only ever calls
    `validator(value)` with one argument. The fix is to return a
    ready-to-use validator that has already "baked in" `limit` via closure,
    so from the outside `max_length(10)` looks and behaves exactly like
    `not_empty`: a plain `str -> ValidationResult` callable.

    Note this is the same problem `functools.partial` solves (Section 1 of
    the lesson) -- pre-fixing an argument ahead of call time. Either a
    closure or `partial` would work here; a hand-written closure is used so
    you can see the mechanism directly, side by side with `partial`-based
    examples elsewhere in this lesson.
    """

    def check(value: str) -> ValidationResult:
        ok = len(value) <= limit
        return ValidationResult(ok, () if ok else (f"must be at most {limit} chars",))

    return check


def run_validators(
    value: str, validators: list[Callable[[str], ValidationResult]]
) -> ValidationResult:
    """
    This is the whole point of the example: `reduce(combine, results, ...)`
    replaces a hand-written accumulator loop with a single expression that
    states the *intent* directly -- "fold every validator's result into one
    combined result, using `combine` as the merge rule, starting from a
    trivially-true empty result."

    Why a generator expression (`results = (validator(value) for validator
    in validators)`) instead of a list comprehension? `reduce` only ever
    needs ONE result at a time (the next one to merge into the running
    accumulator) -- it never needs all of them in memory simultaneously.
    A generator honors that: results are computed lazily, one per `reduce`
    step, instead of eagerly building a list of every ValidationResult
    up front. For 2-3 validators this makes no practical difference; for a
    pipeline with dozens of expensive checks (e.g. ones that hit a
    database), it means a validator only runs when `reduce` actually asks
    for its result.

    Why `ValidationResult(True)` as the initial value (reduce's third
    argument) rather than omitting it? Two reasons. First, correctness: if
    `validators` were ever empty, `reduce` with no initial value raises
    `TypeError` (see the lesson's Deep-Dive Question 1) -- supplying
    `ValidationResult(True)` (valid, no errors) makes "no validators"
    correctly mean "trivially passes," not "crashes." Second, it's the
    correct mathematical identity element for `combine`: combining
    `ValidationResult(True)` with any result `r` always yields `r`
    unchanged, exactly the way `0` is the identity for addition.
    """
    results = (validator(value) for validator in validators)
    return reduce(combine, results, ValidationResult(True))


if __name__ == "__main__":
    validators = [not_empty, max_length(10)]
    # Three deliberately different cases -- fails the first check only,
    # passes both, fails the second check only -- to make it obvious in
    # the printed output that BOTH failure reasons and success are all
    # represented correctly by the same `run_validators` call.
    print(run_validators("", validators))
    print(run_validators("hi", validators))
    print(run_validators("this is way too long", validators))
