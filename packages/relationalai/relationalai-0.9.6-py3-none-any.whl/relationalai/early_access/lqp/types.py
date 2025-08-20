from relationalai.early_access.metamodel import ir as meta
from relationalai.early_access.metamodel import types
from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.lqp.constructors import mk_type, mk_value
from typing import Union

# LQP Integer type limits
INT_MIN = -2**63 # LQP INT is a 64-bit signed integer
INT_MAX = 2**63 - 1 # LQP INT is a 64-bit signed integer
INT128_MIN = -2**127
INT128_MAX = 2**127 - 1
UINT128_MIN = 0
UINT128_MAX = 2**128 - 1

PrimitiveValue = Union[str, int, float, lqp.UInt128, lqp.Int128]

def meta_type_to_lqp(typ: meta.Type) -> lqp.Type:
    if isinstance(typ, meta.UnionType):
        # By this point, unions can only consist of entity types. In the LQP,
        # they are undifferentiated (hashes), so they all merge.
        assert all(types.is_entity_type(t) for t in typ.types), \
            f"Union type {typ} contains non-entity types: " \
            f"{[t for t in typ.types if not types.is_entity_type(t)]}"

        return mk_type(lqp.TypeName.UINT128)
    else:
        assert isinstance(typ, meta.ScalarType)
        if types.is_builtin(typ):
            if typ == types.Int64:
                return mk_type(lqp.TypeName.INT)
            elif typ == types.Int128:
                return mk_type(lqp.TypeName.INT128)
            elif typ == types.Float:
                return mk_type(lqp.TypeName.FLOAT)
            elif typ == types.String:
                return mk_type(lqp.TypeName.STRING)
            elif typ == types.Decimal64:
                return mk_type(lqp.TypeName.DECIMAL, [mk_value(18), mk_value(6)])
            elif typ == types.Decimal128:
                return mk_type(lqp.TypeName.DECIMAL, [mk_value(38), mk_value(10)])
            elif typ == types.Date:
                return mk_type(lqp.TypeName.DATE)
            elif typ == types.DateTime:
                return mk_type(lqp.TypeName.DATETIME)
            elif typ == types.Hash:
                return mk_type(lqp.TypeName.UINT128)
            elif typ == types.RowId:
                return mk_type(lqp.TypeName.UINT128)
            elif typ == types.UInt128:
                return mk_type(lqp.TypeName.UINT128)
            elif typ == types.Number:
                # All types must be specified in the LQP.
                raise Exception("Number type could not be determined.")
            elif types.is_any(typ):
                # All types must be specified in the LQP.
                raise Exception("Type could not be determined.")
            else:
                raise NotImplementedError(f"Unknown builtin type: {typ.name}")
        elif types.is_entity_type(typ):
            return mk_type(lqp.TypeName.UINT128)
        else:
            # Otherwise, the type extends some other type, we use that instead
            assert len(typ.super_types) > 0, f"Type {typ} has no super types"
            assert len(typ.super_types) == 1, f"Type {typ} has multiple super types: {typ.super_types}"
            super_type = typ.super_types[0]
            assert isinstance(super_type, meta.ScalarType), f"Super type {super_type} of {typ} is not a scalar type"
            return meta_type_to_lqp(super_type)

def type_from_constant(arg) -> lqp.Type:
    if isinstance(arg, int):
        name = lqp.TypeName.INT128
    elif isinstance(arg, float):
        name = lqp.TypeName.FLOAT
    elif isinstance(arg, str):
        name = lqp.TypeName.STRING
    elif isinstance(arg, lqp.Int128):
        name = lqp.TypeName.INT128
    elif isinstance(arg, lqp.UInt128):
        name = lqp.TypeName.UINT128
    else:
        raise NotImplementedError(f"Unknown constant type: {type(arg)}")

    return mk_type(name)

def lqp_type_to_sql(arg: lqp.Type) -> str:
    if arg.type_name == lqp.TypeName.INT:
        return "NUMBER(38, 0)"
    elif arg.type_name == lqp.TypeName.FLOAT:
        return "FLOAT"
    elif arg.type_name == lqp.TypeName.STRING:
        return "VARCHAR"
    elif arg.type_name == lqp.TypeName.INT128:
        return "NUMBER(38, 0)"
    elif arg.type_name == lqp.TypeName.UINT128:
        return "NUMBER(38, 0)"
    elif arg.type_name == lqp.TypeName.DATE:
        return "DATE"
    elif arg.type_name == lqp.TypeName.DATETIME:
        return "DATETIME"
    elif arg.type_name == lqp.TypeName.DECIMAL:
        assert len(arg.parameters) == 2, \
            f"DECIMAL type must have 2 parameters, got {arg.parameters}"
        precision = arg.parameters[0].value
        scale = arg.parameters[1].value
        return f"NUMBER({precision}, {scale})"
    else:
        raise NotImplementedError(f"Unknown relational value type: {arg}")
