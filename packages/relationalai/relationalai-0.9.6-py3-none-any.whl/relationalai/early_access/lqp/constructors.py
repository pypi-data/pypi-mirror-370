from typing import Optional, Tuple
from relationalai.early_access.lqp import ir as lqp

def mk_and(args: list[lqp.Formula]) -> lqp.Formula:
    # Flatten nested conjunctions
    if any(isinstance(arg, lqp.Conjunction) for arg in args):
        final_args = []
        for arg in args:
            if isinstance(arg, lqp.Conjunction):
                final_args.extend(arg.args)
            else:
                final_args.append(arg)
        args = final_args

    if len(args) == 1:
        return args[0]

    return lqp.Conjunction(args=args, meta=None)

def mk_or(args: list[lqp.Formula]) -> lqp.Formula:
    # Flatten nested disjunctions
    if any(isinstance(arg, lqp.Disjunction) for arg in args):
        final_args = []
        for arg in args:
            if isinstance(arg, lqp.Disjunction):
                final_args.extend(arg.args)
            else:
                final_args.append(arg)
        args = final_args

    if len(args) == 1:
        return args[0]

    return lqp.Disjunction(args=args, meta=None)

def mk_abstraction(vars: list[Tuple[lqp.Var, lqp.Type]], value: lqp.Formula) -> lqp.Abstraction:
    return lqp.Abstraction(vars=vars, value=value, meta=None)

def mk_exists(vars: list[Tuple[lqp.Var, lqp.Type]], value: lqp.Formula) -> lqp.Formula:
    if len(vars) == 0:
        return value
    abstr = mk_abstraction(vars, value)
    return lqp.Exists(body=abstr, meta=None)

def mk_value(value, cast_type: Optional[lqp.Type] = None) -> lqp.Value:
    return lqp.Value(value=value, cast_type=cast_type, meta=None)

def mk_var(name: str) -> lqp.Var:
    return lqp.Var(name=name, meta=None)

def mk_type(typename: lqp.TypeName, parameters: list[lqp.Value]=[]) -> lqp.Type:
    return lqp.Type(type_name=typename, parameters=parameters, meta=None)

def mk_primitive(name: str, terms: list[lqp.RelTerm]) -> lqp.Primitive:
    return lqp.Primitive(name=name, terms=terms, meta=None)
