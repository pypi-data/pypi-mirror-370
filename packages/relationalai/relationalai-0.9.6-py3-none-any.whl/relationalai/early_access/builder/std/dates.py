from __future__ import annotations
from typing import Any, Union
from datetime import date, datetime

from .. import builder as b

_Date = Union[b.Producer, date]
_DateTime = Union[b.Producer, datetime]
# TODO support DateTime below as well, but this needs e.g. Rel `datetime_year`

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def year(date: _Date) -> b.Expression:
    return _make_expr("date_year", date, b.Int128.ref("res"))

def month(date: _Date) -> b.Expression:
    return _make_expr("date_month", date, b.Int128.ref("res"))

def day(date: _Date) -> b.Expression:
    return _make_expr("date_day", date, b.Int128.ref("res"))

def date_to_datetime(date: _Date, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0, tz: str = "UTC") -> b.Expression:
    _year = year(date)
    _month = month(date)
    _day = day(date)
    return _make_expr("construct_datetime_ms_tz", _year, _month, _day, hour, minute, second, millisecond, tz, b.DateTime.ref("res"))
