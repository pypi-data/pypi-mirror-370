from __future__ import annotations
from typing import Any
from decimal import Decimal as PyDecimal

from .. import builder as b

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

# Coerce a number to Decimal64.
def decimal64(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    if isinstance(value, int):
        value = PyDecimal(str(value))
    if isinstance(value, float):
        value = PyDecimal(str(value))
    return b.ConceptMember(b.Decimal64, value, {})

# Coerce a number to Decimal128.
def decimal128(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    if isinstance(value, int):
        value = PyDecimal(str(value))
    if isinstance(value, float):
        value = PyDecimal(str(value))
    return b.ConceptMember(b.Decimal128, value, {})

# Default decimal to 128 bits.
def decimal(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    return decimal128(value)

def parse_decimal64(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_decimal64", value, b.Decimal64.ref("res"))

def parse_decimal128(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_decimal128", value, b.Decimal128.ref("res"))
