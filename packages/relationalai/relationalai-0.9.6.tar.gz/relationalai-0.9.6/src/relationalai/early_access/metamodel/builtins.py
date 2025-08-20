"""
    Elementary IR relations.
"""
import sys

from . import ir, factory as f
from . import types

from typing import Optional

#
# Relations
#

# Comparators
def _comparator(name: str, input=True):
    overloads = [
        f.relation(name, [f.field("a", type, input), f.field("b", type, input)])
        for type in [types.Bool, types.Int64, types.Int128, types.Float, types.Decimal64, types.Decimal128, types.String, types.Date, types.DateTime, types.Hash, types.EntityTypeVar]
    ]
    return f.relation(name, [f.field("a", types.Any, input), f.field("b", types.Any, input)], overloads=overloads)

gt = _comparator(">")
gte = _comparator(">=")
lt = _comparator("<")
lte = _comparator("<=")
neq = _comparator("!=")
eq = _comparator("=", False)

# Arithmetic operators
def _binary_op(name: str, with_string=False, result_type: Optional[ir.Type]=None):
    overload_types = [types.Int64, types.Int128, types.Float, types.Decimal64, types.Decimal128]
    if with_string:
        overload_types.append(types.String)
    overloads = [
        f.relation(name, [
            f.input_field("a", type),
            f.input_field("b", type),
            f.field("c", result_type if result_type is not None else type)])
        for type in overload_types
    ]

    if with_string:
        return f.relation(name, [f.input_field("a", types.Any), f.input_field("b", types.Any), f.field("c", types.Any)], overloads=overloads)
    else:
        # If strings isn't added, then we're guaranteed to only have number overloads
        result_type = result_type if result_type is not None else types.Number
        return f.relation(name, [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", result_type)], overloads=overloads)

plus = _binary_op("+", with_string=True)
minus = _binary_op("-")
mul = _binary_op("*")
div = f.relation(
    "/",
    [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", types.Number)],
    overloads=[
        f.relation("/", [f.input_field("a", types.Int64), f.input_field("b", types.Int64), f.field("c", types.Float)]),
        f.relation("/", [f.input_field("a", types.Int128), f.input_field("b", types.Int128), f.field("c", types.Float)]),
        f.relation("/", [f.input_field("a", types.Float), f.input_field("b", types.Float), f.field("c", types.Float)]),
        f.relation("/", [f.input_field("a", types.Decimal64), f.input_field("b", types.Decimal64), f.field("c", types.Decimal64)]),
        f.relation("/", [f.input_field("a", types.Decimal128), f.input_field("b", types.Decimal128), f.field("c", types.Decimal128)]),
    ],
)
mod = _binary_op("%")
power = _binary_op("^")

trunc_div = f.relation(
    "//",
    [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", types.Number)],
    overloads=[
        f.relation("//", [f.input_field("a", types.Int64), f.input_field("b", types.Int64), f.field("c", types.Int64)]),
        f.relation("//", [f.input_field("a", types.Int128), f.input_field("b", types.Int128), f.field("c", types.Int128)]),
    ],
)

abs = f.relation(
    "abs",
    [f.input_field("a", types.Number), f.field("b", types.Number)],
    overloads=[
        f.relation("abs", [f.input_field("a", types.Int64), f.field("b", types.Int64)]),
        f.relation("abs", [f.input_field("a", types.Int128), f.field("b", types.Int128)]),
        f.relation("abs", [f.input_field("a", types.Float), f.field("b", types.Float)]),
        f.relation("abs", [f.input_field("a", types.Decimal64), f.field("b", types.Decimal64)]),
        f.relation("abs", [f.input_field("a", types.Decimal128), f.field("b", types.Decimal128)]),
    ],
)

natural_log = f.relation(
    "natural_log",
    [f.input_field("a", types.Number), f.field("b", types.Number)],
    overloads=[
        f.relation("natural_log", [f.input_field("a", types.Int64), f.field("b", types.Float)]),
        f.relation("natural_log", [f.input_field("a", types.Int128), f.field("b", types.Float)]),
        f.relation("natural_log", [f.input_field("a", types.Float), f.field("b", types.Float)]),
        f.relation("natural_log", [f.input_field("a", types.Decimal64), f.field("b", types.Decimal64)]),
        f.relation("natural_log", [f.input_field("a", types.Decimal128), f.field("b", types.Decimal128)]),
    ],
)

sqrt = f.relation(
    "sqrt",
    [f.input_field("a", types.Number), f.field("b", types.Number)],
    overloads=[
        f.relation("sqrt", [f.input_field("a", types.Int64), f.field("b", types.Float)]),
        f.relation("sqrt", [f.input_field("a", types.Int128), f.field("b", types.Float)]),
        f.relation("sqrt", [f.input_field("a", types.Float), f.field("b", types.Float)]),
        f.relation("sqrt", [f.input_field("a", types.Decimal64), f.field("b", types.Decimal64)]),
        f.relation("sqrt", [f.input_field("a", types.Decimal128), f.field("b", types.Decimal128)]),
    ],
)

maximum = f.relation(
    "maximum",
    [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", types.Number)],
    overloads=[
        f.relation("maximum", [f.input_field("a", types.Int64), f.input_field("b", types.Int64), f.field("c", types.Int64)]),
        f.relation("maximum", [f.input_field("a", types.Int128), f.input_field("b", types.Int128), f.field("c", types.Int128)]),
        f.relation("maximum", [f.input_field("a", types.Float), f.input_field("b", types.Float), f.field("c", types.Float)]),
        f.relation("maximum", [f.input_field("a", types.Decimal64), f.input_field("b", types.Decimal64), f.field("c", types.Decimal64)]),
        f.relation("maximum", [f.input_field("a", types.Decimal128), f.input_field("b", types.Decimal128), f.field("c", types.Decimal128)]),
    ],
)

minimum = f.relation(
    "minimum",
    [f.input_field("a", types.Number), f.input_field("b", types.Number), f.field("c", types.Number)],
    overloads=[
        f.relation("minimum", [f.input_field("a", types.Int64), f.input_field("b", types.Int64), f.field("c", types.Int64)]),
        f.relation("minimum", [f.input_field("a", types.Int128), f.input_field("b", types.Int128), f.field("c", types.Int128)]),
        f.relation("minimum", [f.input_field("a", types.Float), f.input_field("b", types.Float), f.field("c", types.Float)]),
        f.relation("minimum", [f.input_field("a", types.Decimal64), f.input_field("b", types.Decimal64), f.field("c", types.Decimal64)]),
        f.relation("minimum", [f.input_field("a", types.Decimal128), f.input_field("b", types.Decimal128), f.field("c", types.Decimal128)]),
    ],
)

isinf = f.relation("isinf", [f.input_field("a", types.Float)])
isnan = f.relation("isnan", [f.input_field("a", types.Float)])

# Strings
concat = f.relation("concat", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.String)])
num_chars = f.relation("num_chars", [f.input_field("a", types.String), f.field("b", types.Int128)])
starts_with = f.relation("starts_with", [f.input_field("a", types.String), f.input_field("b", types.String)])
ends_with = f.relation("ends_with", [f.input_field("a", types.String), f.input_field("b", types.String)])
contains = f.relation("contains", [f.input_field("a", types.String), f.input_field("b", types.String)])
substring = f.relation("substring", [f.input_field("a", types.String), f.input_field("b", types.Int64), f.input_field("c", types.Int64), f.field("d", types.String)])
like_match = f.relation("like_match", [f.input_field("a", types.String), f.field("b", types.String)])
lower = f.relation("lower", [f.input_field("a", types.String), f.field("b", types.String)])
upper = f.relation("upper", [f.input_field("a", types.String), f.field("b", types.String)])

# Dates
date_year = f.relation("date_year", [f.input_field("a", types.Date), f.field("b", types.Int128)])
date_month = f.relation("date_month", [f.input_field("a", types.Date), f.field("b", types.Int128)])
date_day = f.relation("date_day", [f.input_field("a", types.Date), f.field("b", types.Int128)])

# Other
range = f.relation("range", [
    f.input_field("start", types.Int128),
    f.input_field("stop", types.Int128),
    f.input_field("step", types.Int128),
    f.field("result", types.Int128),
])

hash = f.relation("hash", [f.input_field("args", types.AnyList), f.field("hash", types.Hash)])

uuid_to_string = f.relation("uuid_to_string", [f.input_field("a", types.Hash), f.field("b", types.String)])

# Raw source code to be attached to the transaction, when the backend understands this language
raw_source = f.relation("raw_source", [f.input_field("lang", types.String), f.input_field("source", types.String)])

#
# Annotations
#

# indicates a relation is external to the system and, thus, backends should not rename or
# otherwise modify it
external = f.relation("external", [])
external_annotation = f.annotation(external, [])

# indicates an output is meant to be exported
export = f.relation("export", [])
export_annotation = f.annotation(export, [])

# indicates this relation is a concept population
concept_population = f.relation("concept_population", [])
concept_relation_annotation = f.annotation(concept_population, [])

# indicates this relation came in from CDC and will need to be shredded in Rel
from_cdc = f.relation("from_cdc", [])
from_cdc_annotation = f.annotation(from_cdc, [])

# indicates an = lookup that is from a cast operation for value types
from_cast = f.relation("from_cast", [])
from_cast_annotation = f.annotation(from_cast, [])

# indicates the original keys of an output (before they were replaced by a compound key)
output_keys = f.relation("output_keys", [])
output_keys_annotation = f.annotation(output_keys, [])

#
# Aggregations
#
def aggregation(name: str, params: list[ir.Field], overload_types: Optional[list[tuple[ir.Type, ...]]] = None):
    """Defines an aggregation, which is a Relation whose first 2 fields are a projection
    and a group, followed by the params."""
    fields = params
    overloads = []
    if overload_types:
        param_sets = []
        for ts in overload_types:
            param_sets.append([ir.Field(param.name, t, param.input) for param, t in zip(params, ts)])
        overloads = [
            aggregation(name, typed_params, overload_types=None)
            for typed_params in param_sets
        ]
    return f.relation(name, fields, overloads=overloads)

# concat = aggregation("concat", [
#     f.input_field("sep", types.String),
#     f.input_field("over", types.StringSet),
#     f.field("result", types.String)
# ])
# note that count does not need "over" because it counts the projection
count = aggregation("count", [
    f.field("result", types.Int128)
])
stats = aggregation("stats", [
    f.input_field("over", types.Number),
    f.field("std_dev", types.Number),
    f.field("mean", types.Number),
    f.field("median", types.Number),
])
sum = aggregation("sum", [
    f.input_field("over", types.Number),
    f.field("result", types.Number)
], overload_types=[
    (types.Int64, types.Int64),
    (types.Int128, types.Int128),
    (types.Float, types.Float),
    (types.Decimal64, types.Decimal64),
    (types.Decimal128, types.Decimal128),
])
avg = aggregation("avg", [
    f.input_field("over", types.Number),
    f.field("result", types.Number)
], overload_types=[
    (types.Int64, types.Float), # nb. Float because Int / Int is Float
    (types.Int128, types.Float), # nb. Float because Int / Int is Float
    (types.Float, types.Float),
    (types.Decimal64, types.Decimal64),
    (types.Decimal128, types.Decimal128),
])
max = aggregation("max", [
    f.input_field("over", types.Any),
    f.field("result", types.Any)
], overload_types=[
    (types.Int64, types.Int64),
    (types.Int128, types.Int128),
    (types.Float, types.Float),
    (types.Decimal64, types.Decimal64),
    (types.Decimal128, types.Decimal128),
    (types.String, types.String),
    (types.Date, types.Date),
    (types.DateTime, types.DateTime),
    (types.EntityTypeVar, types.EntityTypeVar),
])
min = aggregation("min", [
    f.input_field("over", types.Any),
    f.field("result", types.Any)
], overload_types=[
    (types.Int64, types.Int64),
    (types.Int128, types.Int128),
    (types.Float, types.Float),
    (types.Decimal64, types.Decimal64),
    (types.Decimal128, types.Decimal128),
    (types.String, types.String),
    (types.Date, types.Date),
    (types.DateTime, types.DateTime),
    (types.EntityTypeVar, types.EntityTypeVar),
])

# TODO: these are Rel specific, should be moved from here
# Conversions
string = f.relation("string", [f.input_field("a", types.Any), f.field("b", types.String)])
parse_date = f.relation("parse_date", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.Date)])
parse_datetime = f.relation("parse_datetime", [f.input_field("a", types.String), f.input_field("b", types.String), f.field("c", types.DateTime)])
parse_decimal64 = f.relation("parse_decimal64", [f.input_field("a", types.String), f.field("b", types.Decimal64)])
parse_decimal128 = f.relation("parse_decimal128", [f.input_field("a", types.String), f.field("b", types.Decimal128)])
# Alias parse_decimal128 to parse_decimal
parse_decimal = parse_decimal128

cast = f.relation(
    "cast",
    [
        f.input_field("to_type", types.Any),
        f.input_field("source",  types.Any),
        f.field("target",        types.Any)
    ],
    annos=[from_cast_annotation]
)

# Date construction with less overhead
construct_date = f.relation("construct_date", [f.input_field("year", types.Int64), f.input_field("month", types.Int64), f.input_field("day", types.Int64), f.field("date", types.Date)])
construct_datetime = f.relation("construct_datetime", [f.input_field("year", types.Int64), f.input_field("month", types.Int64), f.input_field("day", types.Int64), f.input_field("hour", types.Int64), f.input_field("minute", types.Int64), f.input_field("second", types.Int64), f.field("datetime", types.DateTime)])
construct_datetime_ms_tz = f.relation("construct_datetime_ms_tz", [f.input_field("year", types.Int64), f.input_field("month", types.Int64), f.input_field("day", types.Int64), f.input_field("hour", types.Int64), f.input_field("minute", types.Int64), f.input_field("second", types.Int64), f.input_field("milliseconds", types.Int64), f.input_field("timezone", types.String), f.field("datetime", types.DateTime)])

# Solver helpers
rel_primitive_solverlib_fo_appl = f.relation("rel_primitive_solverlib_fo_appl", [
    f.input_field("op", types.Int64),
    f.input_field("args", types.AnyList),
    f.field("result", types.String),
])
rel_primitive_solverlib_ho_appl = aggregation("rel_primitive_solverlib_ho_appl", [
    f.input_field("over", types.Any),
    f.field("op", types.Int64),
    f.field("result", types.String),
])
implies = f.relation("implies", [f.input_field("a", types.Bool), f.input_field("b", types.Bool)])
all_different = aggregation("all_different", [f.input_field("over", types.Any)])

#
# Public access to built-in relations
#

def is_builtin(r: ir.Relation):
    return r in builtin_relations or r in builtin_overloads

def is_annotation(r: ir.Relation):
    return r in builtin_annotations

def _compute_builtin_relations() -> list[ir.Relation]:
    module = sys.modules[__name__]
    relations = []
    for name in dir(module):
        builtin = getattr(module, name)
        if isinstance(builtin, ir.Relation) and builtin not in builtin_annotations:
            relations.append(builtin)
    return relations

def _compute_builtin_overloads() -> list[ir.Relation]:
    module = sys.modules[__name__]
    overloads = []
    for name in dir(module):
        builtin = getattr(module, name)
        if isinstance(builtin, ir.Relation) and builtin not in builtin_annotations:
            if builtin.overloads:
                for overload in builtin.overloads:
                    if overload not in builtin_annotations:
                        overloads.append(overload)
    return overloads

# manually maintain the list of relations that are actually annotations
builtin_annotations = [external, export, concept_population, from_cdc, from_cast]
builtin_annotations_by_name = dict((r.name, r) for r in builtin_annotations)

builtin_relations = _compute_builtin_relations()
builtin_overloads = _compute_builtin_overloads()
builtin_relations_by_name = dict((r.name, r) for r in builtin_relations)

string_binary_builtins = [num_chars, starts_with, ends_with, contains, like_match, lower, upper]

date_builtins = [date_year, date_month, date_day]

math_builtins = [abs, *abs.overloads, natural_log, *natural_log.overloads, sqrt, *sqrt.overloads,
                 maximum, *maximum.overloads, minimum, *minimum.overloads, mod, *mod.overloads,
                 power, *power.overloads, trunc_div, *trunc_div.overloads]
