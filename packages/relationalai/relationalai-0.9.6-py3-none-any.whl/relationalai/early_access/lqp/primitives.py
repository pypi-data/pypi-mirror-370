from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.lqp.utils import UniqueNames
from relationalai.early_access.lqp.constructors import mk_primitive, mk_type, mk_var

rel_to_lqp = {
    "=": "rel_primitive_eq",
    "!=": "rel_primitive_neq",
    "%": "rel_primitive_remainder",
    "abs": "rel_primitive_abs",
    "construct_date": "rel_primitive_construct_date",
    "construct_datetime": "rel_primitive_construct_datetime",
    "construct_datetime_ms_tz": "rel_primitive_construct_datetime",
    "hash": "rel_primitive_hash_tuple_uint128",
    "uuid_to_string": "rel_primitive_uuid_string",
    "parse_date": "rel_primitive_parse_date",
    "parse_datetime": "rel_primitive_parse_datetime",
    "parse_decimal": "rel_primitive_parse_decimal",
    "parse_decimal64": "rel_primitive_parse_decimal",
    "parse_decimal128": "rel_primitive_parse_decimal",
    "string": "rel_primitive_string",
    "starts_with": "rel_primitive_starts_with",
    "ends_with": "rel_primitive_ends_with",
    "contains": "rel_primitive_contains",
    "num_chars": "rel_primitive_num_chars",
    "substring": "rel_primitive_substring",
    "like_match": "rel_primitive_like_match",
    "lower": "rel_primitive_lowercase",
    "upper": "rel_primitive_uppercase",
    "concat": "rel_primitive_concat",
    "replace": "rel_primitive_replace",
    "date_year": "rel_primitive_date_year",
    "date_month": "rel_primitive_date_month",
    "date_day": "rel_primitive_date_day",
    "range": "rel_primitive_range",
    "natural_log": "rel_primitive_natural_log",
    "sqrt": "rel_primitive_sqrt",
    # Division is monotype, but only on the input args. Until we distinguish between input
    # and output args, we can't use the same assertions for monotype-ness as the other ops.
    "/": "rel_primitive_divide_monotype",
}

# Mappings of primitive names to their lqp types that represent the raicode expectations.
primitive_types = {
    "date_year": [lqp.TypeName.DATE, lqp.TypeName.INT],
    "date_month": [lqp.TypeName.DATE, lqp.TypeName.INT],
    "date_day": [lqp.TypeName.DATE, lqp.TypeName.INT],
}

agg_to_lqp = {
    "min": "rel_primitive_min",
    "max": "rel_primitive_max",
    "sum": "rel_primitive_add_monotype",
    "count": "rel_primitive_add_monotype", # count is a sum of 1s
    "rel_primitive_solverlib_ho_appl": "rel_primitive_solverlib_ho_appl",
}

rel_to_lqp_monotype = {
    "+": "rel_primitive_add_monotype",
    "-": "rel_primitive_subtract_monotype",
    "*": "rel_primitive_multiply_monotype",
    "<=": "rel_primitive_lt_eq_monotype",
    ">=": "rel_primitive_gt_eq_monotype",
    ">": "rel_primitive_gt_monotype",
    "<": "rel_primitive_lt_monotype",
    "maximum": "rel_primitive_max",
}

def relname_to_lqp_name(name: str) -> str:
    # TODO: do these proprly
    if name in rel_to_lqp:
        return rel_to_lqp[name]
    elif name in rel_to_lqp_monotype:
        return rel_to_lqp_monotype[name]
    else:
        # If we don't have a mapping for the built-in, we just pass it through as-is.
        return name

def is_monotype(name: str) -> bool:
    return name in rel_to_lqp_monotype

# We take the name and type of the variable that we're summing over, so that we can generate
# recognizable names for the variables in the reduce operation and preserve the type.
def lqp_avg_op(names: UniqueNames, op_name: str, sum_name: str, sum_type: lqp.Type) -> lqp.Abstraction:
    count_type = mk_type(lqp.TypeName.INT)
    vars = [
        (mk_var(names.get_name(sum_name)), sum_type),
        (mk_var(names.get_name("counter")), count_type),
        (mk_var(names.get_name(sum_name)), sum_type),
        (mk_var(names.get_name("one")), count_type),
        (mk_var(names.get_name("sum")), sum_type),
        (mk_var(names.get_name("count")), count_type),
    ]

    x1 = vars[0][0]
    x2 = vars[1][0]
    y1 = vars[2][0]
    y2 = vars[3][0]
    sumv = vars[4][0]
    count = vars[5][0]

    body = lqp.Conjunction(
        args=[
            mk_primitive("rel_primitive_add_monotype", [x1, y1, sumv]),
            mk_primitive("rel_primitive_add_monotype", [x2, y2, count])
        ],
        meta=None
    )
    return lqp.Abstraction(vars=vars, value=body, meta=None)

# Default handler for aggregation operations in LQP.
def lqp_agg_op(names: UniqueNames, op_name: str, aggr_arg_name: str, aggr_arg_type: lqp.Type) -> lqp.Abstraction:
    x = mk_var(names.get_name(f"x_{aggr_arg_name}"))
    y = mk_var(names.get_name(f"y_{aggr_arg_name}"))
    z = mk_var(names.get_name(f"z_{aggr_arg_name}"))
    ts = [(x, aggr_arg_type), (y, aggr_arg_type), (z, aggr_arg_type)]

    name = agg_to_lqp.get(op_name, op_name)
    body = mk_primitive(name, [x, y, z])

    return lqp.Abstraction(vars=ts, value=body, meta=None)

def lqp_operator(names: UniqueNames, op_name: str, aggr_arg_name: str, aggr_arg_type: lqp.Type) -> lqp.Abstraction:
    # TODO: Can we just pass through unknown operations?
    if op_name not in agg_to_lqp:
        raise NotImplementedError(f"Unsupported aggregation: {op_name}")

    return lqp_agg_op(names, op_name, aggr_arg_name, aggr_arg_type)
