from __future__ import annotations
from typing import Any, Union
from decimal import Decimal as PyDecimal

from .. import builder as b

_Number = Union[b.Producer, float, int, PyDecimal]
_Integer = Union[b.Producer, int]

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def abs(value: _Number) -> b.Expression:
    return _make_expr("abs", value, b.Number.ref("res"))

def natural_log(value: _Number) -> b.Expression:
    return _make_expr("natural_log", value, b.Number.ref("res"))

def sqrt(value: _Number) -> b.Expression:
    return _make_expr("sqrt", value, b.Number.ref("res"))

def maximum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("maximum", left, right, b.Number.ref("res"))

def minimum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("minimum", left, right, b.Number.ref("res"))

def isinf(value: _Number) -> b.Expression:
    return _make_expr("isinf", value)

def isnan(value: _Number) -> b.Expression:
    return _make_expr("isnan", value)
