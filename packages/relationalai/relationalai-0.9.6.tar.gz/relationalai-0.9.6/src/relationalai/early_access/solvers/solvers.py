from __future__ import annotations
from typing import Any, Union
import textwrap
import uuid

from relationalai.early_access.metamodel.util import ordered_set
from relationalai.early_access.builder import builder as b, std
from relationalai.early_access.rel.executor import RelExecutor

# NOTE(coey) using Solver class from old solvers library to avoid code duplication
from relationalai.experimental.solvers import Solver

_Any = Union[b.Producer, str, float, int]
_String = Union[b.Producer, str]
_Number = Union[b.Producer, float, int]

class SolverModel:
    def __init__(self, model: b.Model, num_type: str):
        assert num_type in ["cont", "int"], "Invalid numerical type, must be 'cont' or 'int'"
        self._model = model # TODO can we remove? only used for _model._to_executor
        self._num_type = num_type
        self._id = next(b._global_id)
        self.variable_relationships = ordered_set()
        prefix_u = f"SolverModel_{self._id}_"
        prefix_l = f"solvermodel_{self._id}_"

        Variable = model.Concept(prefix_u + "Variable")
        self.Variable = Variable
        self.MinObjective = model.Concept(prefix_u + "MinObjective")
        self.MaxObjective = model.Concept(prefix_u + "MaxObjective")
        self.Constraint = model.Concept(prefix_u + "Constraint")

        self._model_info = {
            "num_variables": Variable,
            "num_constraints": self.Constraint,
            "num_min_objectives": self.MinObjective,
            "num_max_objectives": self.MaxObjective,
        }

        res_type = "int" if num_type == "int" else "float"
        self.result_info = model.Relationship("{key:str} has {val:str}", short_name=(prefix_l + "result_info"))
        self.point = model.Relationship(f"{{Variable}} has {{val:{res_type}}}", short_name=(prefix_l + "point"))
        self.points = model.Relationship(f"point {{i:int}} for {{Variable}} has {{val:{res_type}}}", short_name=(prefix_l + "points"))

        b.define(b.RawSource("rel", textwrap.dedent(f"""
        declare {self.MinObjective._name}
        declare {self.MaxObjective._name}
        declare {self.Constraint._name}

        declare {prefix_l}variable_name
        declare {prefix_l}minobjective_name
        declare {prefix_l}maxobjective_name
        declare {prefix_l}constraint_name
        declare {prefix_l}minobjective_serialized
        declare {prefix_l}maxobjective_serialized
        declare {prefix_l}constraint_serialized

        def {prefix_l}minobjective_printed_expr(h, s):
            rel_primitive_solverlib_print_expr({prefix_l}minobjective_serialized[h], {prefix_l}variable_name, s)

        def {prefix_l}maxobjective_printed_expr(h, s):
            rel_primitive_solverlib_print_expr({prefix_l}maxobjective_serialized[h], {prefix_l}variable_name, s)

        def {prefix_l}constraint_printed_expr(h, s):
            rel_primitive_solverlib_print_expr({prefix_l}constraint_serialized[h], {prefix_l}variable_name, s)
        """)))

    def solve_for(self, expr: b.Relationship | b.Fragment, populate: bool = True, **kwargs):
        where = []
        if isinstance(expr, b.Fragment):
            assert expr._select and len(expr._select) == 1 and expr._where, "Fragment input for `solve_for` must have exactly one select and a where clause"
            rel = expr._select[0]
            where = expr._where
        elif isinstance(expr, b.Relationship):
            rel = expr
        else:
            raise ValueError(f"Invalid expression type {type(expr)} for `solve_for`; must be a Relationship or Fragment")

        assert rel._parent, "Relationship for `solve_for` must have a parent"
        assert rel._short_name, "Relationship for `solve_for` must have a short name"
        self.variable_relationships.add(rel)

        ent = b.select(rel._parent).where(*where)
        var = self.Variable.new(entity=ent, relationship=rel._short_name)
        defs = [var]

        # handle optional variable properties
        for (key, val) in kwargs.items():
            if key == "name":
                assert isinstance(val, _String), f"Expected {key} to be a string, got {type(val)}"
                defs.append(var.name(val))
            elif key == "type":
                assert isinstance(val, str), f"Expected {key} to be a string, got {type(val)}"
                assert val in _var_types, f"Invalid variable type {val} for `solve_for`"
                ser = _make_fo_appl_with_res(_var_types[val], var)
                defs.append(self.Constraint.new(serialized=ser))
            elif key in ("lower", "upper", "fixed"):
                assert isinstance(val, _Number), f"Expected {key} to be a number, got {type(val)}"
                op = ">=" if key == "lower" else ("<=" if key == "upper" else "=")
                ser = _make_fo_appl_with_res(_fo_comparisons[op], var, val)
                defs.append(self.Constraint.new(serialized=ser))
            else:
                raise ValueError(f"Invalid keyword argument {key} for `solve_for`")

        b.define(*defs)

        if populate:
            # TODO do something different in future. maybe delete/insert into variable relationships after solve.
            # get variable values from the result point (populated by the solver)
            val = (b.Integer if self._num_type == "int" else b.Float).ref()
            b.define(rel(val)).where(self.point(var, val))
        return var

    # min/max must take a number or a Producer
    def minimize(self, expr: _Number, name: _String | None = None):
        return self._obj(self.MinObjective, expr, name)

    def maximize(self, expr: _Number, name: _String | None = None):
        return self._obj(self.MaxObjective, expr, name)

    def _obj(self, concept: b.Concept, expr: _Number, name):
        sym_expr = _rewrite(expr, self)
        if not sym_expr:
            # expr is not symbolic (a constant)
            # TODO should we warn if objective is constant or do further checks?
            sym_expr = _make_fo_appl_with_res(0, expr)
        elif isinstance(sym_expr, b.ConceptMember):
            # expr probably refers to a single variable, so we need to wrap it for valid protobuf
            sym_expr = _make_fo_appl_with_res(0, sym_expr)
        obj = concept.new(serialized=sym_expr)
        defs = [obj]
        if name is not None:
            defs.append(obj.name(name))
        b.define(*defs)
        return obj

    # satisfy must take a require Fragment
    def satisfy(self, expr: b.Fragment, check: bool = False, name: _String | None = None):
        assert expr._require, "Fragment input for `satisfy` must have a require clause"
        assert not expr._select and not expr._define, "Fragment input for `satisfy` must not have a select or define clause"
        if not check:
            # remove the `require` from the model roots so it is not checked
            b._remove_roots([expr])
        # TODO maybe ensure no variables in `where`s, now `.new`s?
        sym_reqs = []
        for req in expr._require:
            sym_req = _rewrite(req, self)
            assert sym_req, f"Cannot symbolify requirement {req} in `satisfy`"
            sym_reqs.append(sym_req)
        ser = b.union(*sym_reqs) if len(sym_reqs) > 1 else sym_reqs[0]
        # TODO(coey) nested select not working properly on supply_chain, so have to put the where later, for now
        # cons = self.Constraint.new(serialized=b.select(ser).where(*expr._where))
        cons = self.Constraint.new(serialized=ser)
        defs = [cons]
        if name is not None:
            defs.append(cons.name(name))
        b.define(*defs).where(*expr._where)
        return cons

    # print counts of the number of model components
    def summarize(self):
        to_count = [
            self.Variable,
            self.MinObjective.serialized,
            self.MaxObjective.serialized,
            self.Constraint.serialized,
        ]
        counts = b.select(*[(b.count(c) | 0) for c in to_count]).to_df() # TODO(coey) do we need the |0?
        assert counts.shape == (1, len(to_count)), f"Unexpected counts shape {counts.shape}"
        (vars, min_objs, max_objs, cons) = counts.iloc[0]
        print(f"Solver model has {vars} variables, {min_objs} minimization objectives, {max_objs} maximization objectives, and {cons} constraints")
        return None

    # print the variables and components of the model in human-readable format
    def print(self, with_names: bool = False):
        print("Printing solver model.")
        # print variables
        var_df = b.select(self.Variable.name | "_").where(self.Variable).to_df()
        if var_df.empty:
            print("No variables defined in the solver model.")
            return None
        print(f"{var_df.shape[0]} variables:")
        print(var_df.to_string(index=False, header=False))

        # print components
        comps = [
            (self.MinObjective, "minimization objectives"),
            (self.MaxObjective, "maximization objectives"),
            (self.Constraint, "constraints"),
        ]
        for (e, s) in comps:
            sel = [e.name | "", e.printed_expr] if with_names else [e.printed_expr]
            comp_df = b.select(*sel).to_df()
            if not comp_df.empty:
                print(f"{comp_df.shape[0]} {s}:")
                print(comp_df.to_string(index=False, header=False))
        return None

    # solve the model given a solver and solver options
    def solve(self, solver: Solver, log_to_console: bool = False, **kwargs):
        options = kwargs
        options["version"] = 1

        # Validate options.
        for k, v in options.items():
            if not isinstance(k, str):
                raise ValueError(f"Invalid parameter key. Expected string, got {type(k)} for {k}.")
            if not isinstance(v, (int, float, str, bool)):
                raise ValueError(
                    f"Invalid parameter value. Expected string, integer, float, or boolean, got {type(v)} for {k}."
                )

        # Run the solve query and insert the extracted result.
        input_id = uuid.uuid4()
        model_uri = f"snowflake://APP_STATE.RAI_INTERNAL_STAGE/job-inputs/solver/{input_id}/model.binpb"
        sf_input_uri = f"snowflake://job-inputs/solver/{input_id}/model.binpb"
        payload: dict[str, Any] = {"solver": solver.solver_name.lower()}
        payload["options"] = options
        payload["model_uri"] = sf_input_uri

        executor = self._model._to_executor()
        assert isinstance(executor, RelExecutor)
        prefix_l = f"solvermodel_{self._id}_"

        # 1. Materialize the model and store it.
        print("export model")
        b.select(b.count(self.Variable)).to_df() # TODO(coey) weird hack to avoid uninitialized properties error
        executor.execute_raw(textwrap.dedent(f"""
        // TODO maybe only want to pass names if printing - like in old setup
        def model_relation {{
            (:variable, {self.Variable._name});
            (:variable_name, {prefix_l}variable_name);
            (:min_objective, {prefix_l}minobjective_serialized);
            (:max_objective, {prefix_l}maxobjective_serialized);
            (:constraint, {prefix_l}constraint_serialized);
        }}

        @no_diagnostics(:EXPERIMENTAL)
        def model_string {{ rel_primitive_solverlib_model_string[model_relation] }}

        ic model_not_empty("Solver model is empty.") requires not empty(model_string)

        def config[:envelope, :content_type]: "application/octet-stream"
        def config[:envelope, :payload, :data]: model_string
        def config[:envelope, :payload, :path]: "{model_uri}"
        def export {{ config }}
        """))

        # 2. Execute job and wait for completion.
        print("execute solver job")
        job_id = solver._exec_job(payload, log_to_console=log_to_console)

        # 3. Extract result.
        print("extract result")
        extract_str = textwrap.dedent(f"""
        def raw_result {{
            load_binary["snowflake://APP_STATE.RAI_INTERNAL_STAGE/job-results/{job_id}/result.binpb"]
        }}

        ic result_not_empty("Solver result is empty.") requires not empty(raw_result)

        @no_diagnostics(:EXPERIMENTAL)
        def extracted {{ rel_primitive_solverlib_extract[raw_result] }}

        def delete[:{self.result_info._name}]: {self.result_info._name}
        def delete[:{self.point._name}]: {self.point._name}
        def delete[:{self.points._name}]: {self.points._name}

        def insert(:{self.result_info._name}, key, val):
            exists((k) | string(extracted[k], val) and ::std::mirror::lower(k, key))
        """)
        if self._num_type == "int":
            extract_str += textwrap.dedent(f"""
            def insert(:{self.point._name}, var, val):
                exists((x) | extracted(:point, var, x) and
                    ::std::mirror::convert(std::mirror::typeof[Int128], x, val)
                )
            def insert(:{self.points._name}, i, var, val):
                exists((j, x) | extracted(:points, var, j, x) and
                    ::std::mirror::convert(std::mirror::typeof[Int128], j, i) and
                    ::std::mirror::convert(std::mirror::typeof[Int128], x, val)
                )
            """)
        else:
            extract_str += textwrap.dedent(f"""
            def insert(:{self.point._name}, var, val): extracted(:point, var, val)
            def insert(:{self.points._name}, i, var, val):
                exists((j) | extracted(:points, var, j, val) and
                    ::std::mirror::convert(std::mirror::typeof[Int128], j, i)
                )
            """)
        executor.execute_raw(extract_str, readonly=False)

        print("finished solve")
        return None

    # load a particular point index from `points` into `point`
    # so it is accessible from the variable relationship
    def load_point(self, i: int):
        if not isinstance(i, int) and i >= 0:
            raise ValueError(f"Expected nonnegative integer index for point, got {i}")
        executor = self._model._to_executor()
        assert isinstance(executor, RelExecutor)
        executor.execute_raw(textwrap.dedent(f"""
        def delete[:{self.point._name}]: {self.point._name}
        def insert(:{self.point._name}, var, val): {self.points._name}(int128[{i}], var, val)
        """), readonly=False)
        return None

    # print summary of the solver result
    def summarize_result(self):
        to_get = ["error", "termination_status", "solve_time_sec", "objective_value", "solver_version", "result_count"]
        k, v = b.String.ref(), b.String.ref()
        df = b.select(k, v).where(self.result_info(k, v), k.in_(to_get)).to_df()
        assert not df.empty, "No result information"
        print(df.to_string(index=False, header=False))
        return df

    # select variable names and values in the primal result point(s)
    def variable_values(self, multiple: bool = False):
        var = self.Variable.ref()
        val = (b.Integer if self._num_type == "int" else b.Float).ref()
        if multiple:
            i = b.Integer.ref()
            return b.select(i, var.name, val).where(self.points(i, var, val))
        else:
            return b.select(var.name, val).where(self.point(var, val))

    # get scalar result information after solving
    def __getattr__(self, name: str):
        df = None
        if name in self._model_info:
            df = b.select(b.count(self._model_info[name])).to_df()
        elif name in {"error", "termination_status", "solver_version", "printed_model", "solve_time_sec", "objective_value", "result_count"}:
            val = b.String.ref()
            df = b.select(val).where(self.result_info(name, val)).to_df()
        # extract scalar from df
        if df is not None:
            if not df.shape == (1, 1):
                raise ValueError(f"Expected exactly one value for {name}, but df has shape {df.shape}")
            v = df.iloc[0, 0]
            if isinstance(v, str):
                if name == "solve_time_sec":
                    return float(v)
                elif name == "objective_value":
                    return int(v) if self._num_type == "int" else float(v)
                elif name == "result_count":
                    return int(v)
            return v
        return None

# TODO maybe structure rewriting code to be more like the compiler passes rather than in one big if-else
def _rewrite(expr: Any, sm: SolverModel) -> Any:
    if isinstance(expr, (int, float, str)):
        return None
    elif isinstance(expr, b.Ref):
        thing = _rewrite(expr._thing, sm)
        if thing:
            return thing.ref()
        return None
    elif isinstance(expr, b.Concept):
        return None
    elif isinstance(expr, (b.Relationship, b.RelationshipRef, b.RelationshipFieldRef)):
        rel = expr if isinstance(expr, b.Relationship) else expr._relationship
        if rel in sm.variable_relationships:
            return sm.Variable(sm.Variable.ref(), entity=expr._parent, relationship=rel._short_name)
        return None
    elif isinstance(expr, b.Expression):
        op = _rewrite(expr._op, sm) # TODO what cases is this useful for?
        op_rewritten = op is not None
        params_rewritten = False
        params = []
        for p in expr._params:
            rp = _rewrite(p, sm)
            if rp:
                params_rewritten = True
                params.append(rp)
            else:
                params.append(p)
        if op_rewritten:
            assert not params_rewritten, f"Solver rewrites cannot handle expression {expr} with symbolic operator and symbolic parameters"
            return b.Expression(op, *params)
        if not params_rewritten:
            return None
        # some arguments involve solver variables, so rewrite the expression
        assert isinstance(expr._op, b.Relationship), f"Solver rewrites cannot handle expression {expr}"
        op = expr._op._name
        assert isinstance(op, str)
        if op in _fo_operators:
            return _make_fo_appl(_fo_operators[op], *params)
        elif op in _fo_comparisons:
            return _make_fo_appl_with_res(_fo_comparisons[op], *params)
        else:
            raise NotImplementedError(f"Solver rewrites cannot handle operator {op}")
    elif isinstance(expr, b.Aggregate):
        # only the last argument can be symbolic
        start_args = expr._args[:-1]
        for arg in start_args:
            assert not _rewrite(arg, sm), f"Solver rewrites cannot handle expression {expr}; only the last argument can be symbolic"
        sym_arg = _rewrite(expr._args[-1], sm)
        if not sym_arg:
            return None
        op = expr._op._name
        assert isinstance(op, str)
        if op in _ho_operators:
            appl = b.Relationship.builtins["rel_primitive_solverlib_ho_appl"]
            agg = b.Aggregate(appl, *start_args, sym_arg, _ho_operators[op])
            agg._group = expr._group
            agg._where = expr._where
            return agg
        else:
            raise NotImplementedError(f"Solver rewrites cannot handle aggregate operator {op}")
    elif isinstance(expr, b.Union):
        # return union of the symbolified expressions, if any are symbolic
        args_rewritten = False
        args = []
        for arg in expr._args:
            ra = _rewrite(arg, sm)
            if ra:
                args_rewritten = True
                args.append(ra)
            else:
                args.append(arg)
        if args_rewritten:
            return b.union(*args)
        return None
    elif isinstance(expr, b.Fragment):
        # only support selects with one item
        assert not expr._define and not expr._require and len(expr._select) == 1, "Solver rewrites only support fragments with a single select and no define or require clauses"
        sym_select = _rewrite(expr._select[0], sm)
        if sym_select:
            return b.select(sym_select).where(*expr._where)
        return None
    raise NotImplementedError(f"Solver rewrites cannot handle {expr} of type {type(expr)}")


def _make_fo_appl_with_res(op: int, *args: Any):
    return _make_fo_appl(op, *args, b.String.ref("res"))

def _make_fo_appl(op: int, *args: Any):
    assert 2 <= len(args) <= 4
    res = args[-1]
    assert isinstance(res, b.Ref)
    if res._thing != b.String:
        res = b.String.ref("res")
    appl = b.Relationship.builtins["rel_primitive_solverlib_fo_appl"]
    return b.Expression(appl, op, b.TupleArg(args[:-1]), res)

def make_name(*args: _Any, sep: str | None = "_") -> b.Expression:
    if not args:
        raise ValueError("No arguments provided to `make_name`")
    elif len(args) == 1:
        return std.strings.string(args[0])
    elif sep:
        str_args = []
        for a in args:
            str_args.append(std.strings.string(a))
            str_args.append(sep)
        str_args.pop()
    else:
        str_args = map(std.strings.string, args)
    return std.strings.concat(*str_args)

# TODO move to std? need to support normal logical evaluation.
def all_different(*args: Any) -> b.Aggregate:
    return b.Aggregate(b.Relationship.builtins["all_different"], *args)

def implies(left, right) -> b.Expression:
    return b.Expression(b.Relationship.builtins["implies"], left, right)

_var_types = {
    "cont": 40,
    "int": 41,
    "bin": 42,
}

_fo_operators = {
    "+": 10,
    "-": 11,
    "*": 12,
    "/": 13,
    "^": 14,
    "abs": 20,
    "exp": 21,
    "log": 22,
    "range": 50,
}

_fo_comparisons = {
    "=": 30,
    "!=": 31,
    "<=": 32,
    ">=": 33,
    "<": 34,
    ">": 35,
    "implies": 62,
}

_ho_operators = {
    "sum": 80,
    # "product":81,
    "min": 82,
    "max": 83,
    "count": 84,
    "all_different": 90,
}


