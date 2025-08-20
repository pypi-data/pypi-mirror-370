from __future__ import annotations
from typing import Any, Union

from .. import builder as b
from . import dates, math, strings, decimals, integers

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def range(*args: Union[b.Producer, int]) -> b.Expression:
    # supports range(stop), range(start, stop), range(start, stop, step)
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    elif len(args) == 3:
        start, stop, step = args
    else:
        raise ValueError(f"range expects 1, 2, or 3 arguments, got {len(args)}")
    # unlike Python, Rel's range is 1..stop inclusive, so we need to subtract 1 from stop
    return _make_expr("range", start, stop-1, step, b.Integer.ref("res"))

def hash(*args: Any, type=b.Hash) -> b.Expression:
    if len(args) == 0:
        raise ValueError("hash expects at least one argument")
    return _make_expr("hash", b.TupleArg(args), type.ref("res"))

def uuid_to_string(arg:b.Producer|int) -> b.Expression:
    return _make_expr("uuid_to_string", arg, b.String.ref("res"))

__all__ = [
    "range",
    "dates",
    "math",
    "strings",
    "decimals",
    "integers",
]
