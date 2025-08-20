from __future__ import annotations
from typing import Any, Union

from .. import builder as b

_String = Union[b.Producer, str]
_Integer = Union[b.Producer, int]

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

# TODO(coey) can we allow multiple args to this, and convert each to string and concatenate? similar to e.g. julia `string("foo", 1, 'b')`. then we don't need a separate concat function (and concat only works on strings, which is inconvenient).
def string(s: Union[b.Producer, str, float, int]) -> b.Expression:
    return _make_expr("string", s, b.String.ref("res"))

def concat(s0: _String, s1: _String, *args: _String) -> b.Expression:
    res = _make_expr("concat", s0, s1, b.String.ref("res0"))
    for i, s in enumerate(args):
        res = _make_expr("concat", res, s, b.String.ref(f"res{i+1}"))
    return res

def len(s: _String) -> b.Expression:
    return _make_expr("num_chars", s, b.Int128.ref("res"))

def startswith(s0: _String, s1: _String) -> b.Expression:
    return _make_expr("starts_with", s0, s1)

def endswith(s0: _String, s1: _String) -> b.Expression:
    return _make_expr("ends_with", s0, s1)

def contains(s0: _String, s1: _String) -> b.Expression:
    return _make_expr("contains", s0, s1)

def substring(s: _String, start: _Integer, stop: _Integer) -> b.Expression:
    # unlike Python, Rel's range is 1..stop inclusive
    return _make_expr("substring", s, start+1, stop, b.String.ref("res"))

def like(s: _String, pattern: _String) -> b.Expression:
    return _make_expr("like_match", s, pattern)

def lower(s: _String) -> b.Expression:
    return _make_expr("lower", s, b.String.ref("res"))

def upper(s: _String) -> b.Expression:
    return _make_expr("upper", s, b.String.ref("res"))
