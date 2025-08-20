from relationalai.early_access.metamodel import ir, builtins as rel_builtins, helpers, types
from relationalai.early_access.metamodel.visitor import collect_by_type
from relationalai.early_access.lqp import ir as lqp, utils, types as lqp_types
from relationalai.early_access.lqp.primitives import (
    relname_to_lqp_name, lqp_operator, lqp_avg_op, is_monotype, primitive_types
)
from relationalai.early_access.lqp.types import meta_type_to_lqp, type_from_constant
from relationalai.early_access.lqp.constructors import (
    mk_abstraction, mk_and, mk_exists, mk_or, mk_primitive, mk_type, mk_value, mk_var
)
from relationalai.early_access.lqp.utils import TranslationCtx, gen_unique_var
from relationalai.early_access.lqp.validators import assert_valid_input

from math import isinf, isnan
from typing import Tuple, cast, Union, Optional
import re

""" Main access point. Converts the model IR to an LQP transaction. """
def to_lqp(model: ir.Model, fragment_name: bytes, error_attr_ids: Optional[list]) -> tuple[Optional[tuple], Optional[list], lqp.Transaction]:
    assert_valid_input(model)
    ctx = TranslationCtx(model)
    decls: list[lqp.Declaration] = []

    # Extract new pyrel error attributes, if any.
    # These can be used in a subsequent query to report errors.
    # TODO (RAI-40312): Revisit this after reworking compiler/executor interface.
    new_error_ids = _extract_pyrel_error_ids(ctx, model)
    if error_attr_ids is not None:
        # If we have error attributes, we need to add them to the context.
        # This is used to generate the error attributes in the LQP.
        for (rel_id, name) in error_attr_ids:
            ctx.output_ids.append((rel_id, name))


    # LQP only accepts logical tasks
    # These are asserted at init time
    root = cast(ir.Logical, model.root)
    for subtask in root.body:
        assert isinstance(subtask, ir.Logical)
        new_decls = _translate_to_decls(ctx, subtask)
        decls.extend(new_decls)

    reads: list[lqp.Read] = []
    reads.extend(_get_output_reads(ctx.output_ids))

    export_info = None
    if len(ctx.export_ids) > 0:
        export_filename, col_types, export_reads = _get_export_reads(ctx.export_ids)
        reads.extend(export_reads)
        export_info = (export_filename, col_types)

    debug_info = lqp.DebugInfo(id_to_orig_name=ctx.rel_id_to_orig_name, meta=None)
    fragment_id = lqp.FragmentId(id=fragment_name, meta=None)
    fragment = lqp.Fragment(id=fragment_id, declarations=decls, meta=None, debug_info=debug_info)
    define_op = lqp.Define(fragment=fragment, meta=None)

    txn = lqp.Transaction(
        epochs=[
            lqp.Epoch(
                reads=reads,
                writes=[lqp.Write(write_type=define_op, meta=None)],
                meta=None
            )
        ],
        meta=None,
    )

    lqp.validate_lqp(txn)
    return (export_info, new_error_ids, txn)

def _effect_bindings(effect: Union[ir.Output, ir.Update]) -> list[ir.Value]:
    if isinstance(effect, ir.Output):
        # Unions may not return anything. The generated IR contains a None value when this
        # happens. We ignore it here.
        return [v for v in helpers.output_values(effect.aliases) if v]
    else:
        return list(effect.args)

def _get_output_reads(output_ids: list[tuple[lqp.RelationId, str]]) -> list[lqp.Read]:
    reads = []
    for (rel_id, name) in output_ids:
        assert isinstance(rel_id, lqp.RelationId)
        output = lqp.Output(name=name, relation_id=rel_id, meta=None)
        reads.append(lqp.Read(read_type=output, meta=None))
    return reads

def _get_export_reads(export_ids: list[tuple[lqp.RelationId, int, lqp.Type]]) -> tuple[str, list, list[lqp.Read]]:
    reads = []
    csv_columns = []
    col_info = []
    for (col_id, col_num, col_type) in sorted(export_ids, key=lambda x: x[1]):
        col_name = f"col{col_num:03}"
        csv_columns.append(lqp.ExportCSVColumn(column_name=col_name, column_data=col_id, meta=None))
        col_info.append((col_name, col_type))

    # Generate a hashed name based on relation ids
    rel_ids = tuple([id[0] for id in export_ids])
    export_filename = "export_" + str(abs(hash(rel_ids)))

    # Note that the engine will append the transaction id to the export path for access
    # control reasons. So the actual final path will be
    # `.../export/{export_filename}/data_{txn_id}`
    export_path = f"snowflake://APP_STATE.RAI_INTERNAL_STAGE/export/{export_filename}/data"
    export_csv_config = lqp.ExportCSVConfig(
        path=export_path,
        data_columns=csv_columns,
        compression="gzip",
        partition_size=200,
        meta=None,
    )
    reads.append(lqp.Read(read_type=lqp.Export(config=export_csv_config, meta=None), meta=None))
    return (export_filename, col_info, reads)

def _translate_to_decls(ctx: TranslationCtx, rule: ir.Logical) -> list[lqp.Declaration]:
    effects = collect_by_type((ir.Output, ir.Update), rule)
    aggregates = collect_by_type(ir.Aggregate, rule)
    ranks = collect_by_type(ir.Rank, rule)

    # TODO: should this ever actually come in as input?
    if len(effects) == 0:
        return []

    assert len(ranks) == 0 or len(aggregates) == 0, "rules cannot have both aggregates and ranks"

    conjuncts = []
    for task in rule.body:
        if isinstance(task, (ir.Output, ir.Update)):
            continue
        conjuncts.append(_translate_to_formula(ctx, task))

    # Aggregates reduce over the body
    if aggregates or ranks:
        aggr_body = mk_and(conjuncts)
        conjuncts = []
        for aggr in aggregates:
            conjuncts.append(_translate_aggregate(ctx, aggr, aggr_body))
        for rank in ranks:
            conjuncts.append(_translate_rank(ctx, rank, aggr_body))

    return [_translate_effect(ctx, effect, mk_and(conjuncts)) for effect in effects]

# Translates an effect (export, output, or update) into the corresponding def. Note that
# this method only generates the def and not the LQP read operation, which is added later by
# `_get_output_reads` and `_get_export_reads`.
def _translate_effect(ctx: TranslationCtx, effect: Union[ir.Output, ir.Update], body: lqp.Formula) -> lqp.Declaration:
    bindings = _effect_bindings(effect)

    def _is_export(e):
        return isinstance(e, ir.Output) and rel_builtins.export_annotation in e.annotations

    if isinstance(effect, ir.Output):
        projection, eqs, suffix = _translate_output_bindings(ctx, bindings)
        meta_id = effect.id

        if _is_export(effect):
            def_name = "export_relation" + suffix
        else:
            def_name = "output" + suffix

        # Uniquify the output name
        def_name = ctx.def_names.get_name_by_id(meta_id, def_name)
    else:
        projection, eqs = _translate_bindings(ctx, bindings)
        meta_id = effect.relation.id
        def_name = effect.relation.name

    eqs.append(body)
    new_body = mk_and(eqs)

    rel_id = get_relation_id(ctx, def_name, meta_id)

    # Context bookkeeping for exports and outputs
    if _is_export(effect):
        # The row id is the first n-1 elements, and the actual data is the last element. Its
        # type is stored in the first element of the tuple.
        col_type = projection[-1][1]
        _col_num_match = re.search(r"export_relation_col([0-9]+)", def_name)
        assert _col_num_match, f"Could not find column number in suffix: {def_name}"
        col_num = int(_col_num_match.group(1))
        ctx.export_ids.append((rel_id, col_num, col_type))
    elif isinstance(effect, ir.Output):
        ctx.output_ids.append((rel_id, def_name))

    return lqp.Def(
        name = rel_id,
        body = mk_abstraction(projection, new_body),
        attrs = [],
        meta = None,
    )

def _translate_output_bindings(ctx: TranslationCtx, bindings: list[ir.Value]) -> Tuple[list[Tuple[lqp.Var, lqp.Type]], list[lqp.Formula], str]:
    symbol_literals = []
    non_symbols = []
    for binding in bindings:
        if isinstance(binding, ir.Literal) and binding.type == types.Symbol:
            symbol_literals.append(binding.value)
        else:
            non_symbols.append(binding)
    projection, eqs = _translate_bindings(ctx, non_symbols)
    if len(symbol_literals) > 0:
        name_suffix = "_"
        name_suffix += "_".join(symbol_literals)
    else:
        name_suffix = ""

    return projection, eqs, name_suffix

def _translate_rank(ctx: TranslationCtx, rank: ir.Rank, body: lqp.Formula) -> lqp.Formula:
    # Ascending rank is constructed using rel_primitive_sort. If a limit is added to an
    # ascending rank we can use rel_primitive_top for an efficient evaluation.
    #
    # Descending rank is constructed as an ascending sort, then the ascending rank is
    # subtracted from a count of the elements (plus 1 so that we still start at 1).
    # Adding a limit to a descending rank is done by adding a filter of rank <= limit.

    # Limits are the sort plus a filter on rank <= limit.
    if all(o for o in rank.arg_is_ascending):
        ascending = True
    elif all(not o for o in rank.arg_is_ascending):
        ascending = False
    else:
        raise Exception("Mixed orderings in rank are not supported yet.")

    # Filter out the group-by variables, since they are introduced outside the rank.
    input_args, input_eqs = _translate_bindings(ctx, list(rank.args))
    introduced_meta_projs = [arg for arg in rank.projection if arg not in rank.group and arg not in rank.args]
    projected_args, projected_eqs = _translate_bindings(ctx, list(introduced_meta_projs))

    # rank expects an Int128 result, but the primitive will return an Int64 result.
    # we need to set up an intermediary variable to hold the Int64 result, and a cast
    # to convert it to Int128.
    result_var, _ = _translate_term(ctx, rank.result)
    # The primitive will return an Int64 result, so we need a var to hold the intermediary.
    result_64_var = gen_unique_var(ctx, "result_64")
    result_64_type = mk_type(lqp.TypeName.INT)

    cast = lqp.Cast(input=result_64_var, result=result_var, meta=None)

    body = mk_and([body] + input_eqs + projected_eqs)
    abstr_args = input_args + projected_args

    if ascending:
        ranker = _translate_ascending_rank(ctx, rank.limit, result_64_var, body, abstr_args)
    else:
        ranker = _translate_descending_rank(ctx, rank.limit, result_64_var, body, abstr_args)

    return mk_exists([(result_64_var, result_64_type)], mk_and([ranker, cast]))

def _translate_descending_rank(ctx: TranslationCtx, limit: int, result: lqp.Var, body: lqp.Formula, abstr_args) -> lqp.Formula:
    result_var = result
    result_type = mk_type(lqp.TypeName.INT)

    # Rename abstracted args in the body to new variable names
    var_map = {var.name: gen_unique_var(ctx, var.name) for (var, _) in abstr_args}
    body = utils.rename_vars_formula(body, var_map)
    new_abstr_args = [(var_map[var.name], typ) for (var, typ) in abstr_args]

    # Construct a conjunction of the ranking, a counter for the body, a subtraction
    # of the rank from the count and an addition of 1. Wrap this in an abstraction.
    count_res = gen_unique_var(ctx, "count_res")

    # Add one to the count to account for the rank starting at 1.
    one, _, one_eq = constant_to_lqp_var(ctx, 1, types.Int64, "one")
    one_bigger = gen_unique_var(ctx, "one_bigger")
    addition = mk_primitive("rel_primitive_add", [count_res, one, one_bigger])

    # Subtract the rank from the count + 1
    asc_rank = gen_unique_var(ctx, "asc_rank")
    subtraction = mk_primitive("rel_primitive_subtract", [one_bigger, result_var, asc_rank])

    # Construct the ranking
    desc_ranking_terms = [asc_rank] + [v[0] for v in abstr_args]
    ranking = lqp.FFI(
        meta=None,
        name="rel_primitive_sort",
        args=[mk_abstraction(new_abstr_args, body)],
        terms=desc_ranking_terms,
    )

    # Count the number of rows in the body
    count_var, count_type, count_eq = constant_to_lqp_var(ctx, 1, types.Int64, "counter")
    desc_body = mk_and([body, count_eq])
    aggr_abstr_args = new_abstr_args + [(count_var, count_type)]
    count_aggr = lqp.Reduce(
        op=lqp_operator(
            ctx.var_names,
            "count",
            "count",
            mk_type(lqp.TypeName.INT)
        ),
        body=mk_abstraction(aggr_abstr_args, desc_body),
        terms=[count_res],
        meta=None
    )

    # Bring it all together and do the maths.
    ranking = mk_exists(
        vars=[
            (asc_rank, result_type),
            (count_res, result_type),
            (one, result_type),
            (one_bigger, result_type)
        ],
        value=mk_and([ranking, count_aggr, one_eq, addition, subtraction])
    )

    # If there is a limit, we need to add a filter to the ranking.
    # Wrap with a rank <= limit
    if limit != 0:
        limit_term, _ = _translate_term(ctx, limit)
        limiter = mk_primitive("rel_primitive_lt_eq", [result_var, limit_term])
        ranking = mk_and([ranking, limiter])

    return ranking

def _translate_ascending_rank(ctx: TranslationCtx, limit: int, result_var: lqp.Var, body: lqp.Formula, abstr_args) -> lqp.Formula:
    terms = [result_var] + [v[0] for v in abstr_args]

    # Rename abstracted args in the body to new variable names
    var_map = {var.name: gen_unique_var(ctx, var.name) for (var, _) in abstr_args}
    body = utils.rename_vars_formula(body, var_map)
    new_abstr_args = [(var_map[var.name], typ) for (var, typ) in abstr_args]
    sort_abstr = mk_abstraction(new_abstr_args, body)

    if limit == 0:
        return lqp.FFI(
            meta=None,
            name="rel_primitive_sort",
            args=[sort_abstr],
            terms=terms,
        )
    else:
        limit_var, limit_type, limit_eq = constant_to_lqp_var(ctx, limit, types.Int64, "limit")
        limit_abstr = mk_abstraction([(limit_var, limit_type)], limit_eq)
        return lqp.FFI(
            meta=None,
            name="rel_primitive_top",
            args=[sort_abstr, limit_abstr],
            terms=terms,
        )

def _translate_aggregate(ctx: TranslationCtx, aggr: ir.Aggregate, body: lqp.Formula) -> Union[lqp.Reduce, lqp.Formula]:
    # TODO: handle this properly
    aggr_name = aggr.aggregation.name
    supported_aggrs = ("sum", "count", "avg", "min", "max", "rel_primitive_solverlib_ho_appl")
    assert aggr_name in supported_aggrs, f"only support {supported_aggrs} for now, not {aggr.aggregation.name}"

    meta_output_terms = []
    meta_input_terms = []

    for (field, arg) in zip(aggr.aggregation.fields, aggr.args):
        if field.input:
            meta_input_terms.append(arg)
        else:
            meta_output_terms.append(arg)

    output_terms = [_translate_term(ctx, term) for term in meta_output_terms]
    output_vars = [term[0] for term in output_terms]

    body_conjs = [body]
    input_args, input_eqs = _translate_bindings(ctx, meta_input_terms)

    # Filter out the group-by variables, since they are introduced outside the aggregation.
    # Input terms are added later below.
    introduced_meta_projs = [arg for arg in aggr.projection if arg not in aggr.group and arg not in meta_input_terms]
    projected_args, projected_eqs = _translate_bindings(ctx, list(introduced_meta_projs))
    body_conjs.extend(input_eqs)
    body_conjs.extend(projected_eqs)
    abstr_args: list[Tuple[lqp.Var, lqp.Type]] = projected_args + input_args

    if aggr_name == "count":
        assert len(output_terms) == 1, "Count and avg expect a single output variable"
        assert isinstance(meta_output_terms[0], ir.Var)
        # Count sums up "1" for each row. We use the expected output type for the type
        # of the count variable.
        one_var, typ, eq = constant_to_lqp_var(ctx, 1, meta_output_terms[0].type, "one")
        body_conjs.append(eq)
        abstr_args.append((one_var, typ))
        body = mk_and(body_conjs)

    # Average needs to wrap the reduce in Exists(Conjunction(Reduce, div))
    if aggr_name == "avg":
        assert len(output_vars) == 1, "avg should only have one output variable"
        output_var = output_vars[0]

        # Count sums up "1" for each row. We make the reasonably safe assumption that there
        # are less than 2^31 rows in the body.
        one_var, count_type, eq = constant_to_lqp_var(ctx, 1, types.Int64, "one")
        body_conjs.append(eq)
        abstr_args.append((one_var, count_type))
        body = mk_and(body_conjs)

        # The average will produce two output variables: sum and count.
        sum_result = gen_unique_var(ctx, "sum")
        count_result = gen_unique_var(ctx, "count")

        # Second to last is the variable we're summing over.
        (sum_var, sum_type) = abstr_args[-2]

        result = lqp.Reduce(
            op=lqp_avg_op(ctx.var_names, aggr.aggregation.name, sum_var.name, sum_type),
            body=mk_abstraction(abstr_args, body),
            terms=[sum_result, count_result],
            meta=None,
        )

        div = mk_primitive("rel_primitive_divide", [sum_result, count_result, output_var])
        conjunction = mk_and([result, div])

        # Finally, we need to wrap everything in an `exists` to project away the sum and
        # count variables and only keep the result of the division.
        result_terms = [(sum_result, sum_type), (count_result, count_type)]
        return mk_exists(result_terms, conjunction)

    # `input_args`` hold the types of the input arguments, but they may have been modified
    # if we're dealing with a count, so we use `abstr_args` to find the type.
    (aggr_arg, aggr_arg_type) = abstr_args[-1]
    # Group-bys do not need to be handled at all, since they are introduced outside already
    reduce = lqp.Reduce(
        op=lqp_operator(ctx.var_names, aggr.aggregation.name, aggr_arg.name, aggr_arg_type),
        body=mk_abstraction(abstr_args, body),
        terms=output_vars,
        meta=None
    )
    return reduce

def _translate_to_formula(ctx: TranslationCtx, task: ir.Task) -> lqp.Formula:
    if isinstance(task, ir.Logical):
        conjuncts = [_translate_to_formula(ctx, child) for child in task.body]
        return mk_and(conjuncts)
    elif isinstance(task, ir.Lookup):
        return _translate_to_atom(ctx, task)
    elif isinstance(task, ir.Not):
        return lqp.Not(arg=_translate_to_formula(ctx, task.task), meta=None)
    elif isinstance(task, ir.Exists):
        lqp_vars, conjuncts = _translate_bindings(ctx, list(task.vars))
        conjuncts.append(_translate_to_formula(ctx, task.task))
        return mk_exists(lqp_vars, mk_and(conjuncts))
    elif isinstance(task, ir.Construct):
        assert len(task.values) >= 1, "Construct should have at least one value"
        assert isinstance(task.values[0], ir.ScalarType), "Construct should start with a named ScalarType"
        name = task.values[0].name
        terms = [_translate_term(ctx, name)]
        terms.extend([_translate_term(ctx, arg) for arg in task.values[1:]])
        terms.append(_translate_term(ctx, task.id_var))

        return mk_primitive("rel_primitive_hash_tuple_uint128", [v for v, _ in terms])
    elif isinstance(task, ir.Union):
        # TODO: handle hoisted vars if needed
        disjs = [_translate_to_formula(ctx, child) for child in task.tasks]
        return mk_or(disjs)
    elif isinstance(task, (ir.Aggregate, ir.Output, ir.Update)):
        # Nothing to do here, handled in _translate_to_decls
        return mk_and([])
    elif isinstance(task, ir.Rank):
        # Nothing to do here, handled in _translate_to_decls
        return mk_and([])
    else:
        raise NotImplementedError(f"Unknown task type (formula): {type(task)}")

# Only used for translating terms on atoms, which can be specialized values.
def _translate_relterm(ctx: TranslationCtx, term: ir.Value) -> Tuple[lqp.RelTerm, lqp.Type]:
    if isinstance(term, ir.Literal) and term.type == types.Symbol:
        if isinstance(term.value, str):
            value = lqp.Value(value=term.value, cast_type=None, meta=None)
            return lqp.SpecializedValue(value=value, meta=None), meta_type_to_lqp(types.String)
        elif isinstance(term.value, int):
            value = lqp.Value(value=term.value, cast_type=None, meta=None)
            return lqp.SpecializedValue(value=value, meta=None), meta_type_to_lqp(types.Int64)
        else:
            raise NotImplementedError(f"Cannot specialize literal of type {type(term.value)}")
    return _translate_term(ctx, term)

def _translate_term(ctx: TranslationCtx, term: ir.Value) -> Tuple[lqp.Term, lqp.Type]:
    if isinstance(term, ir.Var):
        name = ctx.var_names.get_name_by_id(term.id, term.name)
        t = meta_type_to_lqp(term.type)
        return mk_var(name), t
    elif isinstance(term, ir.Literal):
        if term.type == types.Int128:
            v = lqp.Int128(value=term.value, meta=None)
        else:
            v = term.value
        assert isinstance(v, lqp_types.PrimitiveValue), f"expected primitive value, got {type(term.value)}: {term.value}"
        value = lqp.Value(value=v, cast_type=None, meta=None)
        return value, meta_type_to_lqp(term.type)
    else:
        assert isinstance(term, lqp_types.PrimitiveValue), \
            f"Cannot translate value {term!r} of type {type(term)} to LQP Term; not a PrimitiveValue."
        if isinstance(term, int):
            v = lqp.Int128(value=term, meta=None)
        else:
            v = term
        value = lqp.Value(value=v, cast_type=None, meta=None)
        return value, type_from_constant(term)

def _translate_to_atom(ctx: TranslationCtx, task: ir.Lookup) -> lqp.Formula:
    if task.relation == rel_builtins.cast:
        assert len(task.args) == 3, f"expected three terms for {task.relation.name}, got {len(task.args)}"

        terms = []
        for arg in task.args[1:]:
            term, _ = _translate_relterm(ctx, arg)
            terms.append(term)
        return lqp.Cast(input=terms[0], result=terms[1], meta=None)

    # TODO: want signature not name
    rel_name = task.relation.name
    terms = []
    term_types = []
    for arg in task.args:
        # Handle varargs, which come wrapped in a tuple.
        if isinstance(arg, tuple):
            for vararg in arg:
                term, ty = _translate_relterm(ctx, vararg)
                terms.append(term)
                term_types.append(ty)
        else:
            term, ty = _translate_relterm(ctx, arg)
            terms.append(term)
            term_types.append(ty)

    if rel_builtins.is_builtin(task.relation):
        if task.relation.name == "construct_datetime" and len(terms) == 7:
            # construct_datetime does not provide a timezone or milliseconds so we
            # default to 0 milliseconds and UTC timezone.
            lqp_name = relname_to_lqp_name(task.relation.name)
            extended_terms = [
                *terms[:-1],
                mk_value(0),
                mk_value("UTC"),
                terms[-1],
            ]
            return mk_primitive(lqp_name, extended_terms)
        elif task.relation.name == "like_match":
            # In the like_match API of QB, the variable is the first argument and the pattern the second,
            #   but in Rel, the expected argument order is reversed: pattern first, then variable.
            lqp_name = relname_to_lqp_name(task.relation.name)
            return mk_primitive(lqp_name, terms[::-1])
        elif task.relation.name == "parse_decimal64" and len(terms) == 2:
            # If the builtin for parsing decimals is called directly we will need to add
            # the default parameters of 64 bits and precision 6.
            lqp_name = relname_to_lqp_name(task.relation.name)
            bit_value = lqp.Value(value=64, cast_type=None, meta=None)
            precision_value = lqp.Value(value=6, cast_type=None, meta=None)
            extended_terms = [
                lqp.SpecializedValue(value=bit_value, meta=None),
                lqp.SpecializedValue(value=precision_value, meta=None),
                terms[0],
                terms[1],
            ]
            return mk_primitive(lqp_name, extended_terms)
        elif (
            task.relation.name == "parse_decimal" or
            task.relation.name == "parse_decimal128"
         ) and len(terms) == 2:
            # If the builtin for parsing decimals is called directly we will need to add
            # the default parameters of 128 bits and precision 10.
            lqp_name = relname_to_lqp_name(task.relation.name)
            bit_value = lqp.Value(value=128, cast_type=None, meta=None)
            precision_value = lqp.Value(value=10, cast_type=None, meta=None)
            extended_terms = [
                lqp.SpecializedValue(value=bit_value, meta=None),
                lqp.SpecializedValue(value=precision_value, meta=None),
                terms[0],
                terms[1],
            ]
            return mk_primitive(lqp_name, extended_terms)
        elif task.relation.name == "isinf":
            assert len(terms) == 1, f"expected one term for isinf, got {len(terms)}"
            one_val = mk_value(1.0)
            zero_val = mk_value(0.0)
            return mk_primitive(
                "rel_primitive_divide_monotype",
                [one_val, zero_val, terms[0]],
            )
        elif task.relation.name == "isnan":
            assert len(terms) == 1, f"expected one term for isnan, got {len(terms)}"
            zero_val = mk_value(0.0)
            return mk_primitive(
                "rel_primitive_divide_monotype",
                [zero_val, zero_val, terms[0]],
            )
        elif task.relation.name == "date_year":
            return _cast_primitive(ctx, task.relation.name, terms, term_types)
        elif task.relation.name == "date_month":
            return _cast_primitive(ctx, task.relation.name, terms, term_types)
        elif task.relation.name == "date_day":
            return _cast_primitive(ctx, task.relation.name, terms, term_types)
        else:
            lqp_name = relname_to_lqp_name(task.relation.name)
            if is_monotype(task.relation.name):
                # Make sure that the input terms have the same types
                assert term_types.count(term_types[0]) == len(term_types), \
                    f"Expected all terms to have the same type for monotype operator " \
                    f"`{task.relation.name}` but got {term_types} for terms {terms}"

            return mk_primitive(lqp_name, terms)

    if helpers.is_external(task.relation):
        return lqp.RelAtom(name=task.relation.name, terms=terms, meta=None)

    rid = get_relation_id(ctx, rel_name, task.relation.id)
    return lqp.Atom(name=rid, terms=terms, meta=None)

def _cast_primitive(
        ctx: TranslationCtx,
        name: str,
        terms: list[lqp.RelTerm],
        term_types: list[lqp.Type]
    ) -> lqp.Formula:
    expected = primitive_types.get(name, None)
    if expected is None:
        return mk_primitive(relname_to_lqp_name(name), terms)
    elif expected[-1] == term_types[-1].type_name:
        return mk_primitive(relname_to_lqp_name(name), terms)
    # TODO: check the rest of the terms
    conversion_var = gen_unique_var(ctx, f"result_{expected[-1]}")
    result = terms[-1]
    assert isinstance(result, lqp.Var), f"Expected last term to be a Var, got {type(result)}: {result}"
    terms = [*terms[:-1], conversion_var]

    # Create a cast operation to convert the body to the result type
    cast = lqp.Cast(input=conversion_var, result=result, meta=None)
    primitive = mk_primitive(relname_to_lqp_name(name), terms)
    body = mk_and([primitive, cast])
    return mk_exists([(conversion_var, mk_type(expected[-1]))], body)

def get_relation_id(ctx: TranslationCtx, orig_name: str, metamodel_id: int) -> lqp.RelationId:
    mid_str = str(metamodel_id)
    relation_id = lqp.RelationId(id=utils.lqp_hash(mid_str), meta=None)
    unique_name = ctx.def_names.get_name_by_id(metamodel_id, orig_name)
    ctx.rel_id_to_orig_name[relation_id] = unique_name
    return relation_id

def _translate_bindings(ctx: TranslationCtx, bindings: list[ir.Value]) -> Tuple[list[Tuple[lqp.Var, lqp.Type]], list[lqp.Formula]]:
    lqp_vars = []
    conjuncts = []
    for binding in bindings:
        lqp_var, typ, eq = binding_to_lqp_var(ctx, binding)
        lqp_vars.append((lqp_var, typ))
        if eq is not None:
            conjuncts.append(eq)

    return lqp_vars, conjuncts

def binding_to_lqp_var(ctx: TranslationCtx, binding: ir.Value) -> Tuple[lqp.Var, lqp.Type, Union[None, lqp.Formula]]:
    if isinstance(binding, ir.Var):
        var, typ = _translate_term(ctx, binding)
        assert isinstance(var, lqp.Var)
        return var, typ, None
    elif isinstance(binding, ir.Literal):
        return constant_to_lqp_var(ctx, binding.value, binding.type)
    elif isinstance(binding, lqp_types.PrimitiveValue):
        return constant_to_lqp_var(ctx, binding, None)
    else:
        raise Exception(f"Unsupported binding type: {type(binding)}")

def constant_to_lqp_var(
    ctx: TranslationCtx,
    value: lqp_types.PrimitiveValue,
    type: Optional[ir.Type], name_hint: str = "cvar"
) -> Tuple[lqp.Var, lqp.Type, lqp.Formula]:
    var = gen_unique_var(ctx, name_hint)
    if type is not None:
        typ = meta_type_to_lqp(type)
    else:
        typ = type_from_constant(value)

    # Ensure int values match the requested integer type.
    if typ.type_name == lqp.TypeName.INT and isinstance(value, int):
        assert lqp_types.INT_MIN <= value <= lqp_types.INT_MAX, f"{value} out of range for a 64-bit INT value"
    elif typ.type_name == lqp.TypeName.INT128 and isinstance(value, int):
        assert lqp_types.INT128_MIN <= value <= lqp_types.INT128_MAX, f"{value} out of range for an INT128 value"
        value = lqp.Int128(value=value, meta=None)
    elif typ.type_name == lqp.TypeName.UINT128 and isinstance(value, int):
        assert lqp_types.UINT128_MIN <= value <= lqp_types.UINT128_MAX, f"{value} out of range for an UINT128 value"
        value = lqp.UInt128(value=value, meta=None)

    # Handle special float values. Ensure that NaN == NaN and Inf == Inf, unlike
    # standard IEEE754 behaviour. Note that these match the isnan/isinf primitives.
    if typ.type_name == lqp.TypeName.FLOAT and isinstance(value, float):
        if isnan(value):
            return mk_nan_var(ctx, var)
        elif isinf(value):
            return mk_inf_var(ctx, var)

    value_term = lqp.Value(value=value, cast_type=None, meta=None)
    eq = mk_primitive("rel_primitive_eq", [var, value_term])

    return var, typ, eq

# Do not try to directly translate float("nan"). Instead we generate one by 0.0/0.0
# LQP can accept the float value generated from float("nan") but it will only be comparable
# to itself once we reach the engine.
def mk_nan_var(ctx: TranslationCtx, var:Optional[lqp.Var] = None) -> Tuple[lqp.Var, lqp.Type, lqp.Formula]:
    zero_val = mk_value(0.0)
    nan_var = var if var is not None else gen_unique_var(ctx, "nanvar")
    nan_eq = mk_primitive(
        "rel_primitive_divide_monotype",
        [zero_val, zero_val, nan_var],
    )
    return nan_var, mk_type(lqp.TypeName.FLOAT), nan_eq

# Do not try to directly translate float("inf"). While safer than float("nan") we'll avoid
# relying on the python/protobuf/julia traversals all agreeing and calculate it from
# 1.0/0.0
def mk_inf_var(ctx: TranslationCtx, var:Optional[lqp.Var] = None) -> Tuple[lqp.Var, lqp.Type, lqp.Formula]:
    one_val = mk_value(1.0)
    zero_val = mk_value(0.0)
    inf_var = var if var is not None else gen_unique_var(ctx, "infvar")
    inf_eq = mk_primitive(
        "rel_primitive_divide_monotype",
        [one_val, zero_val, inf_var],
    )
    return inf_var, mk_type(lqp.TypeName.FLOAT), inf_eq

def _extract_pyrel_error_ids(ctx: TranslationCtx, model: ir.Model) -> list[Tuple[lqp.RelationId, str]]:
    effects = collect_by_type(ir.Update, model)
    pyrel_error_attrs = []
    # We use a separate counter here to avoid modifying the current model.
    i = 1
    for effect in effects:
        if "pyrel_error_attrs" not in effect.relation.name:
            continue
        name = f"pyrel_error_attr_{i}"
        meta_id = effect.relation.id
        rel_id = get_relation_id(ctx, name, meta_id)
        pyrel_error_attrs.append((rel_id, name))
        i += 1

    return pyrel_error_attrs
