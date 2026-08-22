"""
Day 4 -- Functional Programming Toolkit: real-world example (Section 5.3 of the lesson).
Run directly: python order_export.py

WHAT THIS FILE DEMONSTRATES
----------------------------
Two problems that show up together constantly in production data-export /
ETL / bulk-API code:

  1. "I need to turn arbitrary domain objects into JSON-safe data, and new
     object types will keep getting added over time by other people, in
     other files, without them having to touch this module."
     -> solved with functools.singledispatch.

  2. "I have a potentially huge collection of records (a DB cursor, a
     generator streaming rows) and I must not load all of it into memory
     at once -- I need to process it in fixed-size chunks."
     -> solved with itertools.islice.

Both are deliberately kept as SEPARATE, small, single-purpose pieces
(`to_json_safe` doesn't know about batching; `batched` doesn't know about
JSON or Order) so that either one could be reused on its own in a different
part of a real codebase.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from functools import singledispatch
from itertools import islice
from typing import Any, Iterable, Iterator


@dataclass(frozen=True)
class Order:
    """
    frozen=True here for the same reason as ValidationResult in
    validation_pipeline.py: an Order flowing through an export pipeline
    should be treated as a snapshot of a fact, not a mutable object that
    some downstream step could accidentally change mid-export. It also
    means Order instances are hashable (useful if you ever need to
    de-duplicate a batch with a set()) and safe to share across threads
    without locking, since nothing can write to them after construction.
    """

    order_id: int
    placed_on: date
    total_cents: int


@singledispatch
def to_json_safe(value: Any) -> Any:
    """
    THE FALLBACK CASE, and it is deliberately defined FIRST and given the
    plain, unadorned `@singledispatch` decorator -- this is what makes it
    the "generic" implementation that every unregistered type falls back
    to. Its job is intentionally trivial: assume the value is something
    `json.dumps` already understands natively (str, int, float, bool,
    None, list, dict) and pass it through untouched.

    Why write this as a dispatcher at all instead of one big function with
    `if isinstance(value, date): ... elif isinstance(value, Order): ...`?
    Because the isinstance-chain version requires every new type to be
    handled by editing THIS function's body -- which means every part of a
    real codebase that wants to add a new exportable type needs write
    access to (and reviewer familiarity with) this exact module. With
    singledispatch, a completely different file can add support for a new
    domain type later just by importing `to_json_safe` and writing its own
    `@to_json_safe.register` -- this function's source never changes. That
    is the "open for extension, closed for modification" property that
    matters once a codebase has more than one contributor.
    """
    return value


@to_json_safe.register
def _(value: date) -> str:
    """
    Registered by TYPE ANNOTATION, not by decorator argument -- the `date`
    in `def _(value: date)` is what tells `singledispatch` which type this
    handler is for; it inspects the function's type hint at registration
    time rather than requiring `@to_json_safe.register(date)`. This is why
    the type hint here isn't just documentation, the way it might be
    elsewhere -- it is load-bearing: remove it and this stops being a
    `date` handler at all.

    The function is named `_` (throwaway name) on purpose: nothing ever
    calls it directly by name -- it's only ever reached through
    `to_json_safe(some_date)` dispatching to it -- so giving it a real name
    would just be a second name for something nobody will use. `_` is the
    conventional Python signal for "this name is intentionally unused."

    `.isoformat()` is used instead of `str(value)` because ISO 8601
    (`"2026-08-01"`) is an unambiguous, locale-independent, round-trippable
    string format -- exactly the property you want for anything that will
    be sent over an API boundary or written to a file another system will
    parse later.
    """
    return value.isoformat()


@to_json_safe.register
def _(value: Order) -> dict[str, Any]:
    """
    This handler shows why singledispatch handlers are allowed to call the
    dispatcher recursively: `asdict(value)` converts the Order dataclass
    into a plain dict, but `payload["placed_on"]` inside that dict is still
    a raw `date` object, not a string -- `asdict` only flattens dataclass
    *structure*, it does not know anything about JSON-safety. Rather than
    duplicating the `date -> isoformat()` logic here, this handler calls
    back into `to_json_safe(value.placed_on)`, which re-dispatches on
    `date` and reuses the handler registered above. This is the same
    principle as Day 3's decorator composition: small pieces that call each
    other, instead of one large function that knows every type's rules in
    one place.

    If Order gained a field of some other custom type in the future, the
    correct fix would be a new `@to_json_safe.register` for that type PLUS
    one more line here delegating to it -- not a hand-written
    if/elif inside this function.
    """
    payload = asdict(value)
    payload["placed_on"] = to_json_safe(value.placed_on)
    return payload


def batched(iterable: Iterable[Any], batch_size: int) -> Iterator[list[Any]]:
    """
    `iterator = iter(iterable)` FIRST, outside the loop, is the detail that
    makes this function correct rather than accidentally infinite or
    accidentally re-starting from the beginning every iteration. `iter()`
    is idempotent on an iterator (calling `iter()` on something that is
    already an iterator just returns that same iterator, per Day 5's
    iterator protocol) but NOT idempotent on an iterable like a list --
    `iter(some_list)` produces a fresh iterator positioned at the start
    every time it's called. By converting to an iterator exactly once, up
    front, every subsequent `islice(iterator, batch_size)` call resumes
    from wherever the previous call left off, instead of starting over
    from element 0 each time.

    `while batch := list(islice(iterator, batch_size)):` is a walrus
    assignment used specifically to avoid computing `islice(...)` twice
    (once to check "is there more data" and again to actually use it).
    `islice(iterator, batch_size)` pulls AT MOST `batch_size` items from
    `iterator`, advancing it by however many items it actually took --
    wrapping that in `list(...)` is what forces those items to actually be
    consumed right now (islice itself is lazy and yields nothing until
    iterated). When `iterator` is finally exhausted, `islice` yields
    nothing, `list(...)` is `[]`, which is falsy, and the `while` loop ends
    -- no manual "have I reached the end" bookkeeping required.

    Crucially, `batched` never does `list(iterable)` on the WHOLE input --
    memory usage stays at O(batch_size), not O(len(iterable)), which is the
    entire point when `iterable` might be a database cursor streaming
    millions of rows.
    """
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


def export_orders(
    orders: Iterable[Order], batch_size: int = 100
) -> Iterator[list[dict[str, Any]]]:
    """
    This function deliberately does NOT know how batching works (that's
    `batched`'s job) and does NOT know how to convert an Order to JSON-safe
    data (that's `to_json_safe`'s job) -- it only knows how to combine the
    two: for each batch `batched` hands it, convert every Order in that
    batch. That separation means either piece can be tested, reused, or
    swapped independently -- e.g. `batched` could just as easily chunk a
    stream of log lines instead of Orders, with zero changes to `batched`
    itself.

    `export_orders` is a generator function (it uses `yield`), which means
    calling it does not immediately process any orders -- it returns an
    iterator, and each batch of orders is only fetched from `orders` and
    converted the moment a caller actually asks for the next batch (e.g.
    via a `for` loop). Combined with `batched`'s O(batch_size) memory use,
    this means a caller could, in principle, stream millions of Order
    records to a JSON API in fixed-size chunks while holding only one
    batch in memory at a time -- Day 5 (Iterators and Generators) goes
    deeper into exactly why `yield` gives you this behavior "for free."
    """
    for batch in batched(orders, batch_size):
        yield [to_json_safe(order) for order in batch]


if __name__ == "__main__":
    sample_orders = [
        Order(order_id=i, placed_on=date(2026, 8, 1), total_cents=1000 + i)
        for i in range(5)
    ]
    # batch_size=2 with 5 orders deliberately produces an UNEVEN last batch
    # (2, 2, 1) so you can see `batched` correctly handles a final partial
    # chunk instead of requiring the input length to divide evenly.
    for batch in export_orders(sample_orders, batch_size=2):
        print(batch)
