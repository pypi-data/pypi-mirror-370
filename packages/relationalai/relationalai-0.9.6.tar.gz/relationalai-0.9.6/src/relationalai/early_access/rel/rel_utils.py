"""
Helpers to generate Rel, many taken from the original PyRel implementation.
"""
from __future__ import annotations
import re
from relationalai.early_access.metamodel import ir, types, factory as f
from decimal import Decimal as PyDecimal

# Rel primitive relations used by the compiler
# TODO: how to deal with varargs?
RelPrimitiveOuterJoin = f.relation("rel_primitive_outer_join", [])

# List of higher order relations in Rel
HIGHER_ORDER = set([
    "::std::common::count",
    "::std::common::sum",
    "::std::common::mean",
    "::std::common::max",
    "::std::common::min",
    "::std::common::sort",
    "::std::common::reverse_sort",
    "::std::common::top",
    "::std::common::bottom",
])

# Decimal scales
DECIMAL64_SCALE = 6
DECIMAL128_SCALE = 10

# Mappings of IR operators to the equivalent in Rel
OPERATORS = {
    # binary
    # TODO: maybe add the binary operators

    # aggregates
    "count": "pyrel_count",
    "sum": "::std::common::sum",
    "avg": "::std::common::mean",
    "max": "::std::common::max",
    "min": "::std::common::min",

    # std
    "range": "::std::common::range",
    "hash": "rel_primitive_hash_tuple_uint128",
    "uuid_to_string": "::std::common::uuid_string",

    # dates
    "date_year": "pyrel_date_year",
    "date_month": "pyrel_date_month",
    "date_day": "pyrel_date_day",
    "construct_datetime_ms_tz": "::std::common::^DateTime",

    # math
    "abs": "::std::common::abs",
    "natural_log": "::std::common::natural_log",
    "sqrt": "std::common::sqrt",
    "maximum": "::std::common::maximum",
    "minimum": "::std::common::minimum",
    "//": "::std::common::trunc_divide",
    "isinf": "::std::common::Infinity",
    "isnan": "::std::common::NaN",

    # strings
    "string": "::std::common::string",
    "concat": "::std::common::concat",
    "starts_with": "::std::common::starts_with",
    "ends_with": "::std::common::ends_with",
    "contains": "::std::common::contains",
    "substring": "::std::common::substring",
    "num_chars": "pyrel_num_chars",
    "like_match": "::std::common::like_match",
    "lower": "::std::common::lowercase",
    "upper": "::std::common::uppercase",

    # decimals
    "parse_decimal64": "pyrel_parse_decimal64",
    "parse_decimal128": "pyrel_parse_decimal128",
    "Decimal64": "pyrel_Decimal64",
    "Decimal128": "pyrel_Decimal128",
}

def rel_operator(ir_op):
    """ Maps an operator from the metamodel IR into the equivalent Rel operator. """
    if ir_op in OPERATORS:
        return OPERATORS[ir_op]
    else:
        return ir_op

def rel_typename(ir_type: ir.Type):
    """ Get the name of the type to use in Rel. """
    if isinstance(ir_type, ir.ScalarType):
        if ir_type == types.Decimal64:
            return 'pyrel_Decimal64'
        elif ir_type == types.Decimal128:
            return 'pyrel_Decimal128'
        elif ir_type == types.Sha1:
            return 'Sha1'
        elif ir_type == types.Enum:
            return '::std::common::UInt128'
        elif ir_type == types.EntityTypeVar:
            return '::std::common::UInt128'
        elif ir_type == types.UInt128:
            return '::std::common::UInt128'
        elif ir_type == types.RowId:
            return '::std::common::UInt128'
        elif ir_type == types.Bool:
            return '::std::common::Boolean'
        elif types.is_builtin(ir_type):
            return f'::std::common::{ir_type.name}'
        elif ir_type.super_types:
            # assuming the compiler narrowed this down somehow
            return rel_typename(ir_type.super_types.some())
        else:
            # user-defined types without a super type are user defined entities
            return '::std::common::UInt128'
    else:
        # TODO: how should we deal with Union types here?
        return '::std::common::Any'

# SEE: REL:      https://docs.relational.ai/rel/ref/lexical-symbols#keywords
#      CORE REL: https://docs.google.com/document/d/12LUQdRed7P5EqQI1D7AYG4Q5gno9uKqy32i3kvAWPCA
RESERVED_WORDS = [
    "and",
    "as",
    "bound",
    "declare",
    "def",
    "else",
    "end",
    "entity",
    "exists",
    "false",
    "for",
    "forall",
    "from",
    "ic",
    "if",
    "iff",
    "implies",
    "in",
    "module",
    "namespace",
    "not",
    "or",
    "requires",
    "then",
    "true",
    "use",
    "where",
    "with",
    "xor"
]

rel_sanitize_re = re.compile(r'[^\w:\[\]\^" ,]|^(?=\d)', re.UNICODE)
unsafe_symbol_pattern = re.compile(r"[^a-zA-Z0-9_]", re.UNICODE)

def sanitize(input_string, is_rel_name_or_symbol = False):
    # Replace non-alphanumeric characters with underscores
    if is_rel_name_or_symbol and "[" in input_string:
        string_parts = input_string.split('[', 1)
        sanitized_name_or_symbol = sanitize_identifier(string_parts[0])
        sanitized_rest = re.sub(rel_sanitize_re, "_", string_parts[1])
        sanitized = f"{sanitized_name_or_symbol}[{sanitized_rest}"
    else:
        if "::" in input_string: # TODO: This is a temp solution to avoid sanitizing the namespace
            sanitized = re.sub(rel_sanitize_re, "_", input_string)
        else:
            sanitized = sanitize_identifier(input_string)

    # Check if the resulting string is a keyword and append an underscore if it is
    if sanitized in RESERVED_WORDS:
        sanitized += "_"

    return sanitized

def sanitize_identifier(name: str) -> str:
    """
    Return a string safe to use as a top level identifier in rel, such as a variable or relation name.

    Args:
        name (str): The input identifier string.

    Returns:
        str: The sanitized identifier string.
    """

    if not name:
        return name

    safe_name = ''.join(c if c.isalnum() else '_' for c in name)
    if safe_name[0].isdigit():
        safe_name = '_' + safe_name
    if  safe_name in RESERVED_WORDS:
        safe_name = safe_name + "_" # preferring the pythonic pattern of `from_` vs `_from`
    return safe_name

def can_represent_as_int64(decimal_value: PyDecimal) -> bool:
    """
    Check if a Python Decimal can be represented exactly as a 64-bit signed integer.

    Args:
        decimal_value (PyDecimal): The input decimal value.

    Returns:
        bool: True if the decimal can be represented as a 64-bit signed integer, False otherwise.
    """
    # 64-bit signed integer range
    INT64_MIN = -9223372036854775808  # -2^63
    INT64_MAX = 9223372036854775807   # 2^63 - 1

    # Check if the decimal has any fractional part
    if decimal_value % 1 != 0:
        return False

    # Convert to integer and check range
    try:
        int_value = int(decimal_value)
        return INT64_MIN <= int_value <= INT64_MAX
    except (ValueError, OverflowError):
        return False
