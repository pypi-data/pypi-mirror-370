from __future__ import annotations

import datetime
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial
from itertools import chain
from typing import Tuple, cast, Optional, Union
from decimal import Decimal as PyDecimal

import math

from relationalai.early_access.metamodel.rewrite import Flatten, ExtractNestedLogicals
from relationalai.early_access.metamodel.visitor import ReadWriteVisitor
from relationalai.util.graph import topological_sort
from relationalai.early_access.metamodel import ir, compiler as c, visitor as v, factory as f, builtins, types, \
    helpers
from relationalai.early_access.metamodel.typer import Checker, InferTypes, typer
from relationalai.early_access.metamodel.builtins import from_cdc_annotation, concept_relation_annotation
from relationalai.early_access.metamodel.types import Hash, String, Number, Int64, Int128, Decimal64, Decimal128, Bool, Date, DateTime, Float
from relationalai.early_access.metamodel.util import FrozenOrderedSet, OrderedSet, frozen, ordered_set, filter_by_type, \
    NameCache
from relationalai.early_access.devmode import sql, rewrite


class Compiler(c.Compiler):
    def __init__(self, skip_denormalization:bool=False):
        rewrites = [
            Checker(),
            ExtractNestedLogicals(),  # before InferTypes to avoid extracting casts
            InferTypes(),
            Flatten(handle_outputs=False),
            rewrite.RecursiveUnion(),
            rewrite.DoubleNegation(),
            rewrite.SortOutputQuery()
        ]
        if not skip_denormalization:
            # group updates, compute SCCs, use Sequence to denote their order
            rewrites.append(rewrite.Denormalize())
        super().__init__(rewrites)
        self.model_to_sql = ModelToSQL()

    def do_compile(self, model: ir.Model, options:dict={}) -> str:
        return str(self.model_to_sql.to_sql(model, options))


@dataclass
class ModelToSQL:
    """ Generates SQL from an IR Model, assuming the compiler rewrites were done. """

    relation_name_cache: NameCache = field(default_factory=NameCache)
    relation_arg_name_cache: NameCache = field(default_factory=NameCache)

    def to_sql(self, model: ir.Model, options:dict) -> sql.Program:
        return sql.Program(self._sort_dependencies(self._generate_statements(model, options)))

    def _generate_statements(self, model: ir.Model, options:dict) -> list[sql.Node]:
        is_duck_db = options.get("is_duck_db", False)
        query_compilation = options.get("query_compilation", False)
        relations = self._get_relations(model, query_compilation)

        self._register_relation_args(relations)
        self._register_external_relations(model)

        statements: list[sql.Node] = []
        for relation in relations:
            statements.append(self._create_table(cast(ir.Relation, relation), if_not_exists=query_compilation, is_duck_db=is_duck_db))
        root = cast(ir.Logical, model.root)
        for child in root.body:
            if isinstance(child, ir.Logical):
                statements.extend(self._create_statement(cast(ir.Logical, child)))
            elif isinstance(child, ir.Union):
                statements.append(self._create_recursive_view(cast(ir.Union, child)))
        return statements

    #--------------------------------------------------
    # SQL Generation
    #--------------------------------------------------
    def _create_table(self, r: ir.Relation, if_not_exists:bool, is_duck_db:bool) -> sql.Node:
        return sql.CreateTable(
            sql.Table(self._relation_name(r),
                list(map(lambda f: sql.Column(self._var_name(r.id, f), self._convert_type(f.type, is_duck_db)), r.fields))
            ), if_not_exists)

    def _create_recursive_view(self, union: ir.Union) -> sql.Node:
        assert len(union.tasks) == 2
        assert isinstance(union.tasks[0], ir.Logical)
        assert isinstance(union.tasks[1], ir.Logical)

        def make_case_select(logical: ir.Logical):
            # TODO - improve the typing info to avoid these casts
            lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
            # TODO - assuming a single update per case
            update = v.collect_by_type(ir.Update, logical).some()

            # TODO - rewriting references to the view, to use the CTE instead, with _rec
            new_lookups = []
            relation = update.relation
            for lookup in lookups:
                if lookup.relation == relation:
                    new_lookups.append(f.lookup(
                        ir.Relation(f"{lookup.relation.name}_rec", lookup.relation.fields,
                                    frozen(), frozen()), lookup.args, lookup.engine))
                else:
                    new_lookups.append(lookup)

            aliases = []
            for i, arg in enumerate(update.args):
                aliases.append((self._var_name(relation.id, relation.fields[i]), arg))
            return self._make_select(new_lookups, aliases)

        # get a representative update
        update = v.collect_by_type(ir.Update, union).some()

        relation = update.relation
        # TODO - maybe this should be more like INSERT INTO a table than a view?
        return sql.CreateView(self._relation_name(relation),
            sql.CTE(True, f"{self._relation_name(relation)}_rec", [self._var_name(relation.id, f) for f in update.relation.fields], [
                make_case_select(cast(ir.Logical, union.tasks[0])),
                make_case_select(cast(ir.Logical, union.tasks[1]))
            ]))

    def _create_statement(self, task: ir.Logical):

        # TODO - improve the typing info to avoid these casts
        nots = cast(list[ir.Not], filter_by_type(task.body, ir.Not))
        lookups = cast(list[ir.Lookup], filter_by_type(task.body, ir.Lookup))
        updates = cast(list[ir.Update], filter_by_type(task.body, ir.Update))
        outputs = cast(list[ir.Output], filter_by_type(task.body, ir.Output))
        logicals = cast(list[ir.Logical], filter_by_type(task.body, ir.Logical))
        constructs = cast(list[ir.Construct], filter_by_type(task.body, ir.Construct))
        ranks = cast(list[ir.Rank], filter_by_type(task.body, ir.Rank))
        aggs = cast(list[ir.Aggregate], filter_by_type(task.body, ir.Aggregate))
        unions = cast(list[ir.Union], filter_by_type(task.body, ir.Union))

        var_to_construct = {c.id_var: c for c in constructs} if constructs else {}

        statements = []
        # TODO - this is simplifying soooo much :crying_blood:
        if updates and not lookups and not nots and not aggs and not logicals and not unions:
            for u in updates:
                r = u.relation
                if r == builtins.raw_source:
                    lang, src = u.args[0], u.args[1]
                    if not (isinstance(lang, str) and lang.lower() == "sql"):
                        logging.warning(f"Unsupported language for RawSource: {lang}")
                        continue
                    if not isinstance(src, str):
                        raise Exception(f"Expected SQL source to be a string, got: {type(src).__name__}")
                    statements.append(sql.RawSource(src))
                else:
                    # TODO: this is assuming that the updates are all static values
                    # Insert static values: INSERT INTO ... SELECT hash(V1, ...), V2, V3 UNION ALL SELECT hash(V4, ...), V5, V6
                    #   We need to use `SELECT` instead of `VALUES` because Snowflake parses and restricts certain expressions in VALUES(...).
                    #       Built-in functions like HASH() or MD5() are often rejected unless used in SELECT.
                    statements.append(
                        sql.Insert(self._relation_name(r), [self._var_name(r.id, f) for f in r.fields], self._get_tuples(task, u), None)
                    )
        elif lookups or outputs or nots or aggs or updates:
            # Some of the lookup relations we wrap into logical and we need to get them out for the SQL compilation.
            #    For example QB `decimal(0)` in IR will look like this:
            #        Logical ^[res]
            #           Exists(vDecimal128)
            #               Logical
            #                   cast(Decimal128, 0, vDecimal128)
            #                   decimal128(vDecimal128, res)
            unions = self._extract_all_of_type_from_logical(task, ir.Union) if logicals else unions
            all_lookups = self._extract_all_of_type_from_logical(task, ir.Lookup) if logicals else lookups

            var_to_union = {
                a: u
                for u in unions
                for t in u.tasks
                if isinstance(t, ir.Lookup)
                for a in t.args
                if isinstance(a, ir.Var)
            } if unions else {}

            if updates:
                # insert values that match a query: INSERT INTO ... SELECT ... FROM ... WHERE ...
                for u in updates:
                    r = u.relation
                    # We shouldn’t create or populate tables for value types that can be directly sourced from existing Snowflake tables.
                    if not self._is_value_type_population_relation(r):
                        select = None
                        if aggs:
                            # After flatten it can be only one aggregation per rule.
                            select = self._make_agg_select(u, all_lookups, aggs[0], nots, unions, constructs)
                        elif ranks:
                            # After flatten it can be only one rank per rule.
                            select = self._make_rank_select(u, all_lookups, ranks[0], nots, unions, constructs)
                        else:
                            aliases = []
                            for i, arg in enumerate(u.args):
                                field_name = self._var_name(r.id, r.fields[i])
                                aliases.append(self._get_alias(field_name, arg, var_to_construct, var_to_union))

                            if not unions:
                                select = self._make_select(all_lookups, aliases, nots, unions, constructs, True)
                            elif lookups:
                                select = self._make_match_select(all_lookups, aliases, unions, nots, constructs, True)
                            else:
                                select = self._make_full_outer_join_select(aliases, unions, constructs, True)

                        statements.append(sql.Insert(self._relation_name(r), [self._var_name(r.id, f) for f in r.fields],
                                                     [], select))
            elif outputs:
                # output a query: SELECT ... FROM ... WHERE ...
                aliases = []
                distinct = False
                for output in outputs:
                    distinct = distinct or output.keys is None
                    for key, arg in output.aliases:
                        aliases.append(self._get_alias(key, arg, var_to_construct, var_to_union))

                if not unions:
                    select = self._make_left_outer_join_select(task, all_lookups, aliases, nots, constructs, distinct)
                elif lookups:
                    select = self._make_match_select(all_lookups, aliases, unions, nots, constructs, distinct)
                else:
                    select = self._make_full_outer_join_select(aliases, unions, constructs, distinct)

                statements.append(select)
        elif logicals:
            for logical in logicals:
                statements.extend(self._create_statement(logical))
        elif not updates and not outputs:
            # Example:
            #   QB:
            #       (
            #         where(Person.age >= 65).define(Senior(Person)) |
            #         where(Person.age >= 18).define(Adult(Person)) |
            #         define(Child(Person))
            #       )
            #   After `flatten` IR will look like this:
            #       Logical
            #           Union
            #               _match_7(person_7)
            #               _match_8(person_7)
            #               _match_9(person_7)
            #
            # Nothing to query or define, we need to skip this task.
            return statements
        else:
            raise Exception(f"Cannot create SQL statement for:\n{task}")
        return statements

    def _make_agg_select(self, update: ir.Update, lookups: list[ir.Lookup], agg: ir.Aggregate,
                         nots: Optional[list[ir.Not]] = None, unions: Optional[list[ir.Union]] = None,
                         constructs: Optional[list[ir.Construct]] = None) -> sql.Select:

        """
        Generate a SQL SELECT for an aggregation using a DISTINCT subquery.

        Example output:
            SELECT
                department, count(v) AS v
            FROM (
                SELECT DISTINCT
                    v0.department, v0.employees AS v
                FROM
                    department_employees AS v0,
                    Department AS v1
                WHERE
                    v0.department = v1.department
            ) GROUP BY department;

        Rationale:
        In the IR, it’s not always explicit whether aggregation should be applied over distinct rows.
        By wrapping the aggregation in a DISTINCT subquery, we ensure correctness regardless of whether
        the original query used `count(...)` or `count(distinct ...)`.

        Compare:

        QB: select(count(Person.name))
        IR:
            Logical
                Logical ^[name=None, person_4=None]
                    Person(person_4)
                    name(person_4, name)
                count([person_4, name], [], [v])
                -> derive _aggregate_1(v)

        QB: select(count(distinct Person.name))
        IR:
            Logical
                Logical ^[name=None]
                    Person(person_4)
                    name(person_4, name)
                count([name], [], [v])
                -> derive _aggregate_1(v)

        Note:
        The key difference is that in the `distinct` case, the grouping variable `person_4` is absent from the projection.
        The subquery pattern unifies both cases by projecting all aggregation arguments, ensuring correctness.
        """

        seen_args = set()
        outputs: list[Union[sql.VarRef, sql.RowNumberVar, int]] = []
        sub_query_outputs: list[Tuple[Optional[str], ir.Value]|Tuple[Optional[str], ir.Value, ir.Task]] = []

        relation = update.relation
        agg_var = agg.args[0] if agg.aggregation == builtins.count else agg.args[1]

        for i, arg in enumerate(update.args):
            if arg not in seen_args:
                field_name = self._var_name(relation.id, relation.fields[i])
                if isinstance(arg, ir.Var) and arg == agg_var:
                    outputs.append(sql.VarRef(f"{agg.aggregation.name}({field_name})", alias=field_name))
                    sub_query_outputs.append((field_name, arg, agg))
                else:
                    outputs.append(sql.VarRef(field_name))
                    sub_query_outputs.append((field_name, arg))
                seen_args.add(arg)

        for arg in agg.projection:
            if arg not in seen_args:
                if agg.aggregation == builtins.count and arg == agg.projection[-1]:
                    continue
                sub_query_outputs.append((None, arg))
                seen_args.add(arg)

        sub_select = self._make_select(lookups, sub_query_outputs, nots, unions, constructs, True)

        group_by: list[sql.VarRef] = [sql.VarRef(var.name) for var in agg.group]

        return sql.Select(False, outputs, sub_select, group_by=group_by)

    def _make_rank_select(self, update: ir.Update, lookups: list[ir.Lookup], rank: ir.Rank,
                         nots: Optional[list[ir.Not]] = None, unions: Optional[list[ir.Union]] = None,
                         constructs: Optional[list[ir.Construct]] = None):

        """
        Generate a SQL SELECT for a rank using a DISTINCT subquery.

        Example output:
            SELECT
                cat, name, ROW_NUMBER() OVER ( ORDER BY name ASC ) as v
            FROM (
                SELECT DISTINCT
                    v0.cat, v1.name
                FROM
                    Cat AS v0, cat_name AS v1
                WHERE
                    v0.cat = v1.cat
            ) LIMIT 10;

        Rationale:
        In the IR, it’s not always explicit whether rank should be applied over distinct rows.
        By wrapping the rank in a DISTINCT subquery, we ensure correctness regardless of whether
        the original query used `rank(...)` or `rank(distinct ...)`.

        Compare:

        QB: select(rank(Cat.name))
        IR:
            Logical
                Cat(cat_5)
                name(cat_5, name)
                rank([cat_5], [], [name'↑'], v)
                -> derive _rank_1(cat_5, name, v)

        QB: select(rank(distinct(Cat.name)))
        IR:
            Logical
                Cat(cat_5)
                name(cat_5, name)
                rank([], [], [name'↑'], v)
                -> derive _rank_1(name, v)

        Note:
        The key difference is that in the `distinct` case, the grouping variable `cat_5` is absent from the projection.
        The subquery pattern unifies both cases by projecting all rank arguments, ensuring correctness.
        """

        seen_args = set()
        outputs: list[Union[sql.VarRef, sql.RowNumberVar, int]] = []
        sub_query_outputs: list[Tuple[Optional[str], ir.Value] | Tuple[Optional[str], ir.Value, ir.Task]] = []

        order_by_vars = []
        for arg, is_ascending in zip(rank.args, rank.arg_is_ascending):
            order_by_vars.append(sql.OrderByVar(arg.name, is_ascending))
        partition_by_vars = [arg.name for arg in rank.group] if rank.group else []

        relation = update.relation

        for i, arg in enumerate(update.args):
            if arg not in seen_args:
                field_name = self._var_name(relation.id, relation.fields[i])
                if isinstance(arg, ir.Var) and arg == rank.result:
                    outputs.append(sql.RowNumberVar(order_by_vars, partition_by_vars, field_name))
                else:
                    outputs.append(sql.VarRef(field_name))
                sub_query_outputs.append((field_name, arg))
                seen_args.add(arg)

        for arg in rank.projection:
            if arg not in seen_args:
                sub_query_outputs.append((None, arg))
                seen_args.add(arg)

        sub_select = self._make_select(lookups, sub_query_outputs, nots, unions, constructs, True)

        return sql.Select(False, outputs, sub_select, limit=rank.limit)

    def _make_match_select(self, lookups: list[ir.Lookup],
                           outputs: list[Tuple[Optional[str], ir.Value] | Tuple[Optional[str], ir.Value, ir.Task]],
                           unions: list[ir.Union], nots: Optional[list[ir.Not]] = None,
                           constructs: Optional[list[ir.Construct]] = None, distinct: bool = False):

        """
        Generate a SQL SELECT statement representing a match operation.

        Example output:
            SELECT
                COALESCE(v2.v0, v3.v0) as v0, v0.name, COALESCE(v4.v0, v5.v0) as v02
            FROM
                person_name AS v0
                JOIN Person AS v1 ON v0.person = v1.person
                LEFT OUTER JOIN _match_3 AS v2 ON v1.person = v2.person
                LEFT OUTER JOIN _match_4 AS v3 ON v1.person = v3.person
                LEFT OUTER JOIN _match_5 AS v4 ON v1.person = v4.person
                LEFT OUTER JOIN _match_6 AS v5 ON v1.person = v5.person
            WHERE
                ( v2.person IS NOT NULL OR v3.person IS NOT NULL ) AND
                ( v4.person IS NOT NULL OR v5.person IS NOT NULL );

        Explanation:
            This query performs a series of joins to gather matching records based on shared keys (`person`).
            - INNER JOINs are used for mandatory relations (e.g. `Person`, `person_name`).
            - LEFT OUTER JOINs are used to include optional match sets from auxiliary `_match_*` tables.
            - `COALESCE(expr1, expr2, ...)` is used to merge values from multiple sources,
                returning the first non-null value among the arguments (or NULL if all are null).
            This is particularly useful for flattening results from union-style matches and preserving partial matches
                in a single SELECT clause.
        """

        var_to_construct = {c.id_var: c for c in constructs} if constructs else {}

        union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]] = self._extract_all_lookups_per_union(unions)

        table_lookups = OrderedSet.from_iterable(t for t in lookups if not builtins.is_builtin(t.relation))
        froms, joins, wheres, sql_vars, var_column, var_lookups = self._extract_match_lookups_metadata(table_lookups, union_lookups)

        builtin_lookups = OrderedSet.from_iterable(t for t in lookups if builtins.is_builtin(t.relation))
        builtin_vars, builtin_wheres = self._resolve_builtins(builtin_lookups, var_lookups, var_column, sql_vars,
                                                              var_to_construct, outputs)

        wheres.extend(builtin_wheres)

        not_null_vars, vars = self._generate_select_output(outputs, builtin_vars, sql_vars, var_column, var_lookups,
                                                           var_to_construct)

        if not_null_vars:
            wheres.extend(sql.NotNull(var) for var in not_null_vars)

        not_exists, _ = self._generate_select_nots(nots, var_lookups, sql_vars, var_column, len(sql_vars))
        wheres.extend(not_exists)

        where = self._process_wheres_clauses(wheres)

        return sql.Select(distinct, vars, froms, where, joins)

    def _make_full_outer_join_select(self,
                                     outputs: list[Tuple[Optional[str], ir.Value] | Tuple[Optional[str], ir.Value, ir.Task]],
                                     unions: list[ir.Union], constructs: Optional[list[ir.Construct]] = None,
                                     distinct: bool = False):

        """
        Generate a SQL SELECT statement representing a match operation that combines multiple sets of data
        (using FULL OUTER JOINs), without additional lookup filtering.

        This method is used when the input IR (Intermediate Representation) does not contain table lookups
        but consists of `Union` operations grouped under a `Logical` node. The goal is to preserve all values
        from each union input while aligning their corresponding fields via outer joins.

        IR Example:
            Logical
                Logical ^[v0=None]
                    Union ^[v0]
                        _match_10(v0)
                        _match_11(v0)
                Logical ^[v0_2=None]
                    Union ^[v0_2]
                        _match_12(v0_2)
                        _match_13(v0_2)
                -> output(v0, v0_2 as 'v02')

        This corresponds to an output schema with two final fields:
        - `v0`, derived from `_match_10` and `_match_11`
        - `v02`, derived from `_match_12` and `_match_13`

        Example output:
            SELECT DISTINCT
                COALESCE(v0.v0, v1.v0) as v0, COALESCE(v2.v0, v3.v0) as v02
            FROM
                _match_10 AS v0
                FULL OUTER JOIN _match_11 AS v1 ON TRUE
                FULL OUTER JOIN _match_12 AS v2 ON TRUE
                FULL OUTER JOIN _match_13 AS v3 ON TRUE;

        Explanation:
            - Each `Union` is compiled into one or more subqueries (e.g. `_match_10`, `_match_11`) that may represent
              disjoint subsets of data.
            - These are combined using `FULL OUTER JOIN` to retain all possible values from each side, including `NULL`s.
            - `COALESCE()` is used to merge values from the joined tables into a single column per output field.
            - This strategy ensures completeness when different subsets may contain different keys or match results.
        """

        var_to_construct = {c.id_var: c for c in constructs} if constructs else {}

        union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]] = self._extract_all_lookups_per_union(unions)
        froms, joins, wheres, sql_vars, var_column, var_lookups = self._extract_union_lookups_metadata(union_lookups)

        not_null_vars, vars = self._generate_select_output(outputs, {}, sql_vars, var_column, var_lookups,
                                                           var_to_construct)

        if not_null_vars:
            wheres.extend(sql.NotNull(var) for var in not_null_vars)

        where = self._process_wheres_clauses(wheres)

        return sql.Select(distinct, vars, froms, where, joins)

    def _make_left_outer_join_select(self, task: ir.Logical, lookups: list[ir.Lookup],
                                     outputs: list[Tuple[Optional[str], ir.Value] | Tuple[Optional[str], ir.Value, ir.Task]],
                                     nots: Optional[list[ir.Not]] = None, constructs: Optional[list[ir.Construct]] = None,
                                     distinct: bool = False) -> sql.Select:

        """
        Generate a SQL SELECT statement from an output query by combining INNER JOIN and LEFT OUTER JOIN clauses
        based on the IR structure.

        ### JOIN Rules:

        1. **Top-level lookups** (direct children of the root `Logical`) always use **INNER JOIN**.

        2. **LEFT OUTER JOIN** is used for a lookup if:
           - It appears inside a nested `Logical`, and
           - The corresponding variable is hoisted with a `None` value in that `Logical`.
           - Example: `id(student, id)` is translated as a LEFT OUTER JOIN if the `Logical` hoists `id=None`.

        3. If a variable is hoisted with `None` in one `Logical`, but used in another lookup that is hoisted without `None`,
            the corresponding join becomes **INNER JOIN**.
           - This resolves ambiguity when a lookup's output variable is reused meaningfully elsewhere.

        ---

        ### IR Example 1 (with LEFT OUTER JOIN):

        IR:
            Logical
                Logical
                    Student(student)
                    goes_at(student, school)
                    subject(school, subject)
                    desc(subject, desc)
                    desc = "English"
                    Logical ^[id=None]
                        id(student, id)
                    Logical ^[name=None, course=None]
                        attends(student, course)
                        instructor(course, instructor)
                        name(instructor, name)
                    -> output[student, course, subject](id, name, desc)

        SQL Output:
            SELECT
                v0.id, v3.name, v7.desc
            FROM
                Student AS v4
                JOIN student_goes_at AS v5 ON v4.student = v5.student
                JOIN school_subject AS v6 ON v5.school = v6.school
                JOIN subject_desc AS v7 ON v6.subject = v7.subject
                LEFT OUTER JOIN student_id AS v0 ON v5.student = v0.student
                LEFT OUTER JOIN student_attends AS v1 ON v5.student = v1.student
                LEFT OUTER JOIN course_instructor AS v2 ON v1.course = v2.course
                LEFT OUTER JOIN instructor_name AS v3 ON v2.instructor = v3.instructor
            WHERE
                v7.desc = 'English';

        ---

        ### IR Example 2 (with NOT EXISTS):

        IR:
            Logical
                Not
                    Logical
                        Logical ^[person, age]
                            _union_1(person, age)
                Person(person)
                Logical ^[name=None]
                    name(person, name)
                Logical ^[age=None]
                    age(person, age)
                -> output[person](name, age)

        Note: Even though `age` is hoisted with `None`, it is also used in `_union_1` which is hoisted without `None`
        (i.e., `^[person, age]`). Therefore, `age(person, age)` is compiled as an INNER JOIN.

        SQL Output:
            SELECT
                v0.name,
                v1.age
            FROM
                Person AS v2
                JOIN person_name AS v0 ON v2.person = v0.person
                JOIN person_age AS v1 ON v2.person = v1.person
            WHERE
                NOT EXISTS ( SELECT 1 FROM _union_1 AS v3 WHERE v3.person = v0.person AND v3.age = v1.age );

        ---
        """

        var_to_construct = {c.id_var: c for c in constructs} if constructs else {}

        table_lookups = OrderedSet.from_iterable(t for t in lookups if not builtins.is_builtin(t.relation))
        froms, joins, wheres, sql_vars, var_column, var_lookups = (
            self._extract_left_outer_joins_lookups_metadata(task, table_lookups, nots))

        builtin_lookups = OrderedSet.from_iterable(t for t in lookups if builtins.is_builtin(t.relation))
        builtin_vars, builtin_wheres = self._resolve_builtins(builtin_lookups, var_lookups, var_column, sql_vars,
                                                              var_to_construct, outputs)
        wheres.extend(builtin_wheres)

        _, vars = self._generate_select_output(outputs, builtin_vars, sql_vars, var_column, var_lookups, var_to_construct)

        not_exists, _ = self._generate_select_nots(nots, var_lookups, sql_vars, var_column, len(sql_vars))
        wheres.extend(not_exists)

        where = self._process_wheres_clauses(wheres)

        return sql.Select(distinct, vars, froms, where, joins)

    def _make_select(self, lookups: list[ir.Lookup],
                     outputs: list[Tuple[Optional[str], ir.Value]|Tuple[Optional[str], ir.Value, ir.Task]],
                     nots: Optional[list[ir.Not]] = None, unions: Optional[list[ir.Union]] = None,
                     constructs: Optional[list[ir.Construct]] = None, distinct: bool = False) -> sql.Select:

        var_to_construct = {c.id_var: c for c in constructs} if constructs else {}

        union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]] = self._extract_all_lookups_per_union(unions)
        all_lookups = lookups + list(chain.from_iterable(union_lookups.values()))

        table_lookups = OrderedSet.from_iterable(t for t in all_lookups if not builtins.is_builtin(t.relation))
        froms, wheres, sql_vars, var_column, var_lookups = self._extract_lookups_metadata(table_lookups)

        builtin_lookups = OrderedSet.from_iterable(t for t in all_lookups if builtins.is_builtin(t.relation))
        builtin_vars, builtin_wheres = self._resolve_builtins(builtin_lookups, var_lookups, var_column, sql_vars,
                                                              var_to_construct, outputs)
        wheres.extend(builtin_wheres)

        wheres.extend(self._generate_where_clauses(var_lookups, var_column, sql_vars, union_lookups))

        not_null_vars, vars = self._generate_select_output(outputs, builtin_vars, sql_vars, var_column,
                                                                  var_lookups, var_to_construct)

        if not_null_vars:
            wheres.extend(sql.NotNull(var) for var in not_null_vars)

        not_exists, _ = self._generate_select_nots(nots, var_lookups, sql_vars, var_column, len(sql_vars))
        wheres.extend(not_exists)

        where = self._process_wheres_clauses(wheres)

        return sql.Select(distinct, vars, froms, where)

    def _extract_lookups_metadata(self, lookups: OrderedSet[ir.Lookup], start_index: int = 0):
        froms: list[sql.From] = []
        wheres: list[sql.Expr] = []
        sql_vars: dict[ir.Lookup, str] = dict()  # one var per table lookup
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = dict()
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = defaultdict(OrderedSet)
        i = start_index

        for lookup in lookups:
            varname = f"v{i}"
            froms.append(sql.From(self._relation_name(lookup.relation), varname))
            sql_vars[lookup] = varname
            self._process_lookup_args(lookup, sql_vars, var_column, var_lookups, wheres)
            i += 1

        return froms, wheres, sql_vars, var_column, var_lookups

    def _extract_match_lookups_metadata(self, lookups: OrderedSet[ir.Lookup],
                                         union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]], start_index: int = 0):
        wheres: list[sql.Expr] = []
        sql_vars: dict[ir.Lookup, str] = dict()  # one var per table lookup
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = dict()
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = defaultdict(OrderedSet)
        i = start_index

        def process_lookups(lookup_set: OrderedSet[ir.Lookup]):
            nonlocal i
            for lookup in lookup_set:
                sql_vars[lookup] = f"v{i}"
                self._process_lookup_args(lookup, sql_vars, var_column, var_lookups, wheres)
                i += 1

        # Step 1: assign aliases and populate helper mappings
        process_lookups(lookups)
        for values in union_lookups.values():
            process_lookups(values)

        # Step 2: build joins
        used_lookups = ordered_set()
        first_lookup = next(iter(lookups))
        used_lookups.add(first_lookup)
        froms: list[sql.From] = []
        joins: list[sql.Join] = []

        # Start with the first table as the root FROM
        froms.append(sql.From(self._relation_name(first_lookup.relation), sql_vars[first_lookup]))

        def _process_joins(lookup: ir.Lookup, is_left_join: bool = False):
            # Try to find a shared variable with any *latest* used lookup
            join_conditions = []
            lookup_not_null_conditions = []

            for arg in lookup.args:
                if isinstance(arg, ir.Var) and arg in var_lookups:
                    for other_lookup in reversed(list(used_lookups)):  # reversed: prioritize most recent join
                        if other_lookup in var_lookups[arg]:
                            left_alias = sql_vars[other_lookup]
                            right_alias = sql_vars[lookup]

                            left_field = self._var_name(other_lookup.relation.id, var_column[(arg, other_lookup)])
                            right_field = self._var_name(lookup.relation.id, var_column[(arg, lookup)])

                            left_var = f"{left_alias}.{left_field}"
                            right_var = f"{right_alias}.{right_field}"

                            join_conditions.append(sql.Terminal(f"{left_var} = {right_var}"))

                            if is_left_join:
                                lookup_not_null_conditions.append(sql.NotNull(right_var))

                            break  # stop on first recent match

            if join_conditions:
                on = sql.And(join_conditions) if len(join_conditions) > 1 else join_conditions[0]
                join = sql.LeftOuterJoin(self._relation_name(lookup.relation), sql_vars[lookup], on) if is_left_join \
                    else sql.Join(self._relation_name(lookup.relation), sql_vars[lookup], on)
                joins.append(join)

                if is_left_join:
                    return sql.And(lookup_not_null_conditions) if len(lookup_not_null_conditions) > 1 else lookup_not_null_conditions[0]
                else:
                    used_lookups.add(lookup)
                    return None
            else:
                raise ValueError(f"No join condition found for lookup: {lookup}")

        # Add JOINs based on shared variables
        for lookup in lookups:
            if lookup not in used_lookups:
                _process_joins(lookup)

        # Add LEFT JOINs based on shared variables
        for values in union_lookups.values():
            not_null_conditions = []
            for lookup in values:
                if lookup not in used_lookups:
                    lookup_condition = _process_joins(lookup, is_left_join=True)
                    not_null_conditions.append(lookup_condition)

            if not_null_conditions:
                wheres.append(sql.Or(not_null_conditions))

        return froms, joins, wheres, sql_vars, var_column, var_lookups

    def _extract_union_lookups_metadata(self, lookups: dict[ir.Union, OrderedSet[ir.Lookup]], start_index: int = 0):
        wheres: list[sql.Expr] = []
        sql_vars: dict[ir.Lookup, str] = {}
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = {}
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = defaultdict(OrderedSet)
        froms: list[sql.From] = []
        joins: list[sql.Join] = []
        used_lookups = ordered_set()

        i = start_index
        first_lookup_handled = False

        for values in lookups.values():
            for lookup in values:
                sql_vars[lookup] = f"v{i}"
                self._process_lookup_args(lookup, sql_vars, var_column, var_lookups, wheres)
                i += 1

                if not first_lookup_handled:
                    # Use this as the base FROM
                    froms.append(sql.From(self._relation_name(lookup.relation), sql_vars[lookup]))
                    used_lookups.add(lookup)
                    first_lookup_handled = True
                else:
                    # Join the rest
                    joins.append(sql.FullOuterJoin(self._relation_name(lookup.relation), sql_vars[lookup]))

        return froms, joins, wheres, sql_vars, var_column, var_lookups

    def _extract_left_outer_joins_lookups_metadata(self, task: ir.Logical, lookups: OrderedSet[ir.Lookup],
                                                   nots: Optional[list[ir.Not]] = None, start_index: int = 0):
        wheres: list[sql.Expr] = []
        sql_vars: dict[ir.Lookup, str] = dict()  # one var per table lookup
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = dict()
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = defaultdict(OrderedSet)

        # Step 1: assign aliases and populate helper mappings
        i = start_index
        for lookup in lookups:
            sql_vars[lookup] = f"v{i}"
            self._process_lookup_args(lookup, sql_vars, var_column, var_lookups, wheres)
            i += 1

        froms: list[sql.From] = []
        joins: list[sql.Join] = []
        full_context = ordered_set()

        # Choose a root FROM table
        first_lookup = next(iter(lookups))
        froms.append(sql.From(self._relation_name(first_lookup.relation), sql_vars[first_lookup]))
        full_context.add(first_lookup)

        @dataclass(frozen=True)
        class JoinMetadata:
            on: Optional[sql.Expr] = None
            inner_join: bool = False

        joins_metadata: dict[ir.Lookup, JoinMetadata] = {}
        not_null_vars: set[ir.Var] = self._extract_all_not_null_vars_from_nots(nots)

        def _process_joins(lookup: ir.Lookup, context: OrderedSet[ir.Lookup], inner_join: bool = True):
            join_conditions = []
            seen_pairs = set()

            # We want most recent joins first from context, then from full_context
            search_context = list(reversed(context)) + [
                lk for lk in reversed(full_context) if lk not in context
            ]

            for arg in lookup.args:
                inner_join = arg in not_null_vars or inner_join
                if isinstance(arg, ir.Var) and arg in var_lookups:
                    for other_lookup in search_context:
                        if other_lookup in var_lookups[arg]:
                            right_alias = sql_vars[lookup]
                            left_alias = sql_vars[other_lookup]

                            right_field = self._var_name(lookup.relation.id, var_column[(arg, lookup)])
                            left_field = self._var_name(other_lookup.relation.id, var_column[(arg, other_lookup)])

                            pair = (left_alias, left_field, right_alias, right_field)
                            if pair not in seen_pairs:
                                seen_pairs.add(pair)
                                join_conditions.append(sql.Terminal(f"{left_alias}.{left_field} = {right_alias}.{right_field}"))
                            break  # stop at first matching lookup

            on = None
            if join_conditions:
                on = sql.And(join_conditions) if len(join_conditions) > 1 else join_conditions[0]

            join_metadata = joins_metadata.get(lookup)

            if join_metadata:
                # Upgrade to inner join only if previously marked as left outer join
                if inner_join and not join_metadata.inner_join:
                    joins_metadata[lookup] = JoinMetadata(on, inner_join)
            else:
                joins_metadata[lookup] = JoinMetadata(on, inner_join)

        def _process_logical(logical: ir.Logical, parent_context: Optional[OrderedSet[ir.Lookup]] = None):
            # Step 1: Prepare null variables from hoisted defaults
            null_vars = {
                v.var for v in (logical.hoisted or [])
                if isinstance(v, ir.Default) and v.value is None
            }

            # Step 2: Create a working context from parent_context
            context = OrderedSet.from_iterable(parent_context) if parent_context else ordered_set()

            # Step 3: Process all sub-tasks
            for sub_task in logical.body:
                if isinstance(sub_task, ir.Logical):
                    _process_logical(sub_task, context)
                elif isinstance(sub_task, ir.Lookup):
                    lookup = cast(ir.Lookup, sub_task)
                    if lookup != first_lookup and not builtins.is_builtin(lookup.relation):
                        inner_join = False if null_vars else True
                        _process_joins(lookup, context, inner_join)
                        context.add(lookup)
                        full_context.add(lookup)

        _process_logical(task, full_context)

        for lookup, metadata in joins_metadata.items():
            if metadata.inner_join:
                joins.append(sql.Join(self._relation_name(lookup.relation), sql_vars[lookup], metadata.on))
            else:
                joins.append(sql.LeftOuterJoin(self._relation_name(lookup.relation), sql_vars[lookup], metadata.on))

        return froms, joins, wheres, sql_vars, var_column, var_lookups

    def _process_lookup_args(self, lookup: ir.Lookup, sql_vars: dict[ir.Lookup, str],
                             var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field],
                             var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]], wheres: list[sql.Expr]):
        relation = lookup.relation
        for j, arg in enumerate(lookup.args):
            rel_field = relation.fields[j]
            if isinstance(arg, ir.Var):
                var_column[arg, lookup] = rel_field
                var_lookups[arg].add(lookup)
            # case when Literal is used as a relation argument: `test(1, x)`
            elif isinstance(arg, (int, str, float, bool, ir.Literal)):
                ref = f"{sql_vars[lookup]}.{self._var_name(relation.id, rel_field)}"
                wheres.append(sql.Terminal(f"{ref} = {self._convert_value(arg, False)}"))

    def _var_reference(self, var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]], sql_vars: dict[ir.Lookup, str],
                       var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field], v) -> str:
        if isinstance(v, ir.Var):
            # TODO - assuming the built-in reference was grounded elsewhere
            lookup = var_lookups[v].some()
            return f"{sql_vars[lookup]}.{self._var_name(lookup.relation.id, var_column[(v, lookup)])}"
        elif isinstance(v, ir.Literal):
            return self._convert_value(v.value)
        elif isinstance(v, datetime.date):
            return f"cast('{v}' as date)"
        return f"'{v}'" if isinstance(v, str) else str(v)

    def _resolve_builtin_var(self, builtin_vars: dict[ir.Var, ir.Value], var):
        # We need recursive lookup because it maybe a case when we need to join more than 2 lookups.
        #    For example QB `a != decimal(0)` in IR will look like this:
        #        Logical ^[res]
        #           Exists(vDecimal128)
        #               Logical
        #                   cast(Decimal128, 0, vDecimal128)
        #                   decimal128(vDecimal128, res)
        #        a != res
        #    But we need to convert it to `a != 0` in SQL.
        if isinstance(var, ir.Var) and var in builtin_vars:
            val = builtin_vars[var]
            return self._resolve_builtin_var(builtin_vars, val) if isinstance(val, ir.Var) else val
        return var

    def _resolve_construct_var(self, reference, resolve_builtin_var, construct: ir.Construct):
        # Generate constructions like hash(`x`, `y`, TABLE_ALIAS.COLUMN_NAME)
        elements = []
        for val in construct.values:
            val = resolve_builtin_var(val)
            if isinstance(val, ir.Var):
                elements.append(reference(val))
            else:
                elements.append(self._convert_value(val, True))
        return f"hash({', '.join(elements)})"

    def _resolve_builtins(self, builtin_lookups: OrderedSet[ir.Lookup], var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]],
                          var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field], sql_vars: dict[ir.Lookup, str],
                          var_to_construct: dict[ir.Var, ir.Construct],
                          outputs: Optional[list[Tuple[Optional[str], ir.Value]|Tuple[Optional[str], ir.Value, ir.Task]]] = None):

        wheres: list[sql.Expr] = []
        builtin_vars: dict[ir.Var, ir.Value] = {}

        output_vars = {
            output[1]
            for output in outputs or []
            if isinstance(output[1], ir.Var)
        }

        intermediate_builtin_vars: set[ir.Var] = {
            arg for lookup in builtin_lookups
            for arg in lookup.args
            if isinstance(arg, ir.Var) and arg not in var_lookups
        }

        reference = partial(self._var_reference, var_lookups, sql_vars, var_column)
        resolve_builtin_var = partial(self._resolve_builtin_var, builtin_vars)

        for lookup in self._sort_builtin_lookups(list(builtin_lookups), output_vars):
            args = lookup.args
            relation = lookup.relation
            relation_name = self._relation_name(relation)

            if relation == builtins.substring:
                assert len(args) == 4, f"Expected 4 args for `strings.substring`, got {len(args)}: {args}"

                # Unpack and process arguments
                lhs_raw, from_idx_raw, to_idx_raw, output = args
                assert isinstance(output, ir.Var), "Fourth argument (output) must be a variable"
                from_idx = self._convert_value(from_idx_raw)
                to_idx = self._convert_value(to_idx_raw)

                # Resolve the left-hand side expression
                lhs = lhs_raw if lhs_raw in intermediate_builtin_vars else reference(lhs_raw)
                left = self._var_to_expr(lhs, reference, resolve_builtin_var, var_to_construct) \
                    if isinstance(lhs_raw, ir.Var) else str(lhs)

                # Calculate substring length: SQL is 1-based and end-inclusive
                substring_len = int(to_idx) - int(from_idx) + 1
                assert substring_len >= 0, f"Invalid substring range: from {from_idx} to {to_idx}"

                expr = f"substring({left}, {from_idx}, {substring_len})"
                builtin_vars[output] = expr
            elif relation == builtins.cast:
                assert len(args) == 3, f"Expected 3 args for `cast`, got {len(args)}: {args}"

                _, original_raw, result = args
                assert isinstance(result, ir.Var), "Third argument (result) must be a variable"

                original = original_raw if original_raw in intermediate_builtin_vars else reference(original_raw)
                builtin_vars[result] = original
            elif relation in (builtins.isnan, builtins.isinf):
                arg_expr = self._var_to_expr(args[0], reference, resolve_builtin_var, var_to_construct)
                expr = "cast('NaN' AS DOUBLE)" if relation == builtins.isnan else "cast('Infinity' AS DOUBLE)"
                wheres.append(sql.Terminal(f"{arg_expr} = {expr}"))
            else:
                # Assuming infix binary or ternary operators here
                lhs_raw, rhs_raw = args[0], args[1]
                lhs = lhs_raw if lhs_raw in intermediate_builtin_vars else reference(lhs_raw)
                rhs = rhs_raw if rhs_raw in intermediate_builtin_vars else reference(rhs_raw)
                if relation in builtins.string_binary_builtins:
                    left = self._var_to_expr(lhs_raw, reference, resolve_builtin_var, var_to_construct)
                    if relation == builtins.num_chars and isinstance(rhs_raw, ir.Var):
                        builtin_vars[rhs_raw] = f"length({left})"
                    elif relation == builtins.lower and isinstance(rhs_raw, ir.Var):
                        builtin_vars[rhs_raw] = f"lower({left})"
                    elif relation == builtins.upper and isinstance(rhs_raw, ir.Var):
                        builtin_vars[rhs_raw] = f"upper({left})"
                    else:
                        right = self._var_to_expr(rhs_raw, reference, resolve_builtin_var, var_to_construct)
                        if relation == builtins.starts_with:
                            expr = f"concat({right}, '%')" if isinstance(rhs_raw, ir.Var) else f"'{right}%'"
                        elif relation == builtins.ends_with:
                            expr = f"concat('%', {right})" if isinstance(rhs_raw, ir.Var) else f"'%{right}'"
                        elif relation == builtins.like_match:
                            expr = right if isinstance(rhs_raw, ir.Var) else f"'{right}'"
                        elif relation == builtins.contains:
                            expr = f"concat('%', {right}, '%')" if isinstance(rhs_raw, ir.Var) else f"'%{right}%'"
                        else:
                            raise Exception(f"Unsupported string builtin relation: {relation}")
                        wheres.append(sql.Like(left, expr))
                elif relation == builtins.string and isinstance(rhs_raw, ir.Var):
                    if isinstance(lhs_raw, ir.Var) and typer.to_base_primitive(lhs_raw.type) == DateTime:
                        # Convert DateTime to string in the ISO 8601 format.
                        #TODO: This works only in SF and we need to handle it differently for the DuckDB engine.
                        builtin_vars[rhs_raw] = f"""to_varchar({lhs}, 'YYYY-MM-DD"T"HH24:MI:SS.FF3')"""
                    else:
                        builtin_vars[rhs_raw] = lhs
                elif relation in builtins.date_builtins and isinstance(rhs_raw, ir.Var):
                    expr_map = {
                        builtins.date_year: "year",
                        builtins.date_month: "month",
                        builtins.date_day: "day"
                    }
                    expr = expr_map.get(relation)
                    builtin_vars[rhs_raw] = f"{expr}({lhs})"
                elif relation in builtins.math_builtins:
                    result_var = rhs_raw
                    rel_name = relation.name
                    left = self._var_to_expr(lhs_raw, reference, resolve_builtin_var, var_to_construct)
                    if rel_name == builtins.abs.name:
                        expr = f"abs({left})"
                    elif rel_name == builtins.natural_log.name:
                        expr = f"ln({left})"
                    elif rel_name == builtins.sqrt.name:
                        expr = f"sqrt({left})"
                    elif rel_name in (builtins.minimum.name, builtins.maximum.name, builtins.trunc_div.name,
                                      builtins.power.name, builtins.mod.name):
                        assert len(args) == 3, f"Expected 3 args for {relation}, got {len(args)}: {args}"

                        result_var = args[2]
                        right = self._var_to_expr(rhs_raw, reference, resolve_builtin_var, var_to_construct)

                        if rel_name == builtins.minimum.name:
                            expr = f"least({left}, {right})"
                        elif rel_name == builtins.maximum.name:
                            expr = f"greatest({left}, {right})"
                        elif rel_name == builtins.trunc_div.name:
                            expr = f"trunc({left} / {right})"
                        elif rel_name == builtins.power.name:
                            expr = f"power({left}, {right})"
                        else:
                            expr = f"mod({left}, {right})"
                    else:
                        raise Exception(f"Unsupported math builtin relation: {relation}")
                    assert isinstance(result_var, ir.Var), (
                        f"Expected `ir.Var` type for the result of `{relation}`, "
                        f"but got `{type(result_var).__name__}`: {result_var}"
                    )
                    builtin_vars[result_var] = expr
                elif helpers.is_from_cast(lookup) and isinstance(rhs_raw, ir.Var):
                    # For the `from cast` relations we keep the raw var, and we will ground it later.
                    builtin_vars[rhs_raw] = lhs_raw
                elif isinstance(lhs, ir.Var) and lhs in output_vars:
                    builtin_vars[lhs] = self._var_to_expr(rhs, reference, resolve_builtin_var, var_to_construct)
                elif isinstance(rhs, ir.Var) and rhs in output_vars:
                    builtin_vars[rhs] = self._var_to_expr(lhs, reference, resolve_builtin_var, var_to_construct)
                elif isinstance(lhs, ir.Var) and lhs in intermediate_builtin_vars and lhs not in (builtin_vars | var_to_construct):
                    # Example IR:
                    #   Logical
                    #       Logical ^[v0]
                    #           int = 2
                    #           Logical ^[res=None]
                    #               Logical ^[res]
                    #                   cast(Float, int, int_Float)
                    #                   res = 2.1 * int_Float
                    #           v0 = res
                    #       -> derive _match_1(v0)
                    #
                    # In this example, the `int` variable is an intermediate result produced by the `=` (assignment) builtin.
                    # We must retain this value in the `builtin_vars` mapping so it can be used when compiling the `cast`.
                    # Ultimately, this allows us to fully resolve the final expression: `v0 = 2.1 * 2`.
                    builtin_vars[lhs] = self._var_to_expr(rhs, reference, resolve_builtin_var, var_to_construct)
                elif isinstance(rhs, ir.Var) and rhs in intermediate_builtin_vars and rhs not in (builtin_vars | var_to_construct):
                    # Please see the example above but in this case it will be `2 = int` builtin lookup instead of `int = 2`.
                    builtin_vars[rhs] = self._var_to_expr(lhs, reference, resolve_builtin_var, var_to_construct)
                else:
                    left = self._var_to_expr(lhs, reference, resolve_builtin_var, var_to_construct)
                    right = self._var_to_expr(rhs, reference, resolve_builtin_var, var_to_construct)

                    if len(args) == 3:
                        out_var = args[2]
                        if isinstance(out_var, ir.Var):
                            out_var = resolve_builtin_var(out_var)
                            if relation != builtins.concat:
                                expr = f"({left} {relation_name} {right})"
                            else:
                                expr = f"{relation_name}({left}, {right})"
                            if isinstance(out_var, ir.Var):
                                # For example, when this is an intermediate result
                                # example: c = a - b in the IR is (a - b = d) and (d = c)
                                builtin_vars[out_var] = expr
                            else:
                                # This means that var was already grounded and we can add WHERE clause.
                                wheres.append(sql.Terminal(f"{expr} = {out_var}"))
                        else:
                            raise Exception(
                                f"Expected `ir.Var` type for the relation `{relation}` output but got `{type(out_var).__name__}`: {out_var}"
                            )
                    else:
                        # Replace intermediate vars with disjoined expressions
                        expr = f"{left} {relation_name} {right}"
                        wheres.append(sql.Terminal(expr))

        # After handling all builtins we need to generate where statements for args with single lookup.
        for arg, lookup_set in var_lookups.items():
            if len(lookup_set) == 1:
                lookup = lookup_set[0]
                column = var_column[cast(ir.Var, arg), lookup]
                column_name = self._var_name(lookup.relation.id, column)
                ref = f"{sql_vars[lookup]}.{column_name}"
                # case when we have a builtin operation as a relation argument
                #   example: `test(a - 1, b)` and we are handling here `a - 1` arg.
                if arg in builtin_vars:
                    rhs_ref = resolve_builtin_var(arg)
                    if isinstance(rhs_ref, ir.Var):
                        rhs = reference(rhs_ref) if rhs_ref in var_lookups else rhs_ref.name
                    else:
                        rhs = str(rhs_ref)
                    wheres.append(sql.Terminal(f"{ref} = {rhs}"))

                # IR example:
                #   Logical
                #       construct(Manager, "manager_id", "JoeManager", manager_2)
                #       Manager_to_Employee(manager_2, manager_3)
                #       → derive ranking(manager_3, 10)
                elif arg in var_to_construct:
                    rhs = self._resolve_construct_var(reference, resolve_builtin_var, var_to_construct[arg])
                    wheres.append(sql.Terminal(f"{ref} = {rhs}"))

        return builtin_vars, wheres

    def _generate_where_clauses(self, var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]],
                                var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field], sql_vars: dict[ir.Lookup, str],
                                union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]]):
        # Reverse mapping: lookup -> union
        lookup_to_union: dict[ir.Lookup, ir.Union] = {}
        for union, lookups in union_lookups.items():
            for lu in lookups:
                lookup_to_union[lu] = union

        wheres: list[sql.Expr] = []
        plain_refs_by_var: dict[ir.Var, list[str]] = defaultdict(list)
        all_union_members: dict[str, dict[ir.Var, str]] = defaultdict(dict)
        for arg, lookup_set in var_lookups.items():
            # if there are 2 lookups for the same variable, we need a join
            if len(lookup_set) > 1:
                # Step 1: Collect all lookups by union member or plain
                for lu in lookup_set:
                    col = var_column[arg, lu]
                    col_name = self._var_name(lu.relation.id, col)

                    matched_union = lookup_to_union.get(lu)
                    if matched_union:
                        for u_lu in union_lookups[matched_union]:
                            u_ref = f"{sql_vars[u_lu]}.{col_name}"
                            all_union_members[sql_vars[u_lu]][arg] = u_ref
                    else:
                        ref = f"{sql_vars[lu]}.{col_name}"
                        plain_refs_by_var[arg].append(ref)

        # Step 2: Build AND chain of plain lookups
        and_clauses = []
        for refs in plain_refs_by_var.values():
            # join variable references pairwise (e.g. "x.id = y.id AND y.id = z.id")
            for lhs, rhs in zip(refs, refs[1:]):
                and_clauses.append(sql.Terminal(f"{lhs} = {rhs}"))

        # Step 3: Build one OR clause across union members
        or_groups: list[sql.Expr] = []
        for member_ref_map in all_union_members.values():
            expressions = []
            for arg_var, rhs in member_ref_map.items():
                plain_refs = plain_refs_by_var.get(arg_var)
                if plain_refs:
                    lhs = plain_refs[-1]  # last plain ref for that var
                    expressions.append(sql.Terminal(f"{lhs} = {rhs}"))
            if expressions:
                or_groups.append(sql.And(expressions) if len(expressions) > 1 else expressions[0])

        wheres.extend(and_clauses)
        if or_groups:
            wheres.append(sql.Or(or_groups))

        return wheres

    def _process_wheres_clauses(self, wheres: list[sql.Expr]) -> Optional[sql.Where]:
        # conjunction of not_wheres
        if len(wheres) == 0:
            where = None
        elif len(wheres) == 1:
            where = sql.Where(wheres[0])
        else:
            where = sql.Where(sql.And(wheres))
        return where

    def _generate_select_output(self, outputs: list[Tuple[Optional[str], ir.Value]|Tuple[Optional[str], ir.Value, ir.Task]],
                                builtin_vars: dict[ir.Var, ir.Value], sql_vars: dict[ir.Lookup, str],
                                var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field],
                                var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]],
                                var_to_construct: dict[ir.Var, ir.Construct]):

        reference = partial(self._var_reference, var_lookups, sql_vars, var_column)
        resolve_builtin_var = partial(self._resolve_builtin_var, builtin_vars)

        def handle_lookup_var(var):
            lookup = var_lookups[var].some()
            relation = lookup.relation
            var_name = sql_vars[lookup]
            column_name = self._var_name(relation.id, var_column[var, lookup])
            vars.append(sql.VarRef(var_name, column_name, alias))
            if from_cdc_annotation in relation.annotations:
                not_null_vars.add(f"{var_name}.{column_name}")

        def handle_construct(construct):
            # Generate constructions like hash(`x`, `y`, TABLE_ALIAS.COLUMN_NAME)
            elements = []
            for val in construct.values:
                if val in builtin_vars:
                    val = resolve_builtin_var(val)
                if isinstance(val, ir.Var):
                    if val in var_to_construct:
                        elements.append(handle_construct(var_to_construct[val]))
                    else:
                        lookup = var_lookups[val].some()
                        column_name = self._var_name(lookup.relation.id, var_column[val, lookup])
                        lookup_var = f"{sql_vars[lookup]}.{column_name}"
                        elements.append(lookup_var)
                        if from_cdc_annotation in lookup.relation.annotations:
                            not_null_vars.add(lookup_var)
                else:
                    elements.append(self._convert_value(val, True))
            return f"hash({', '.join(elements)})"

        # finally, compute what the select will return
        vars = []
        not_null_vars = ordered_set()
        for output in outputs:
            alias, var = output[0], output[1]
            task = output[2] if len(output) > 2 else None
            if isinstance(var, ir.Var):
                if var in var_lookups and not task:
                    handle_lookup_var(var)
                elif var in builtin_vars:
                    var_ref = resolve_builtin_var(var)
                    if var_ref in var_lookups:
                        # Case: result of `cast` variable
                        handle_lookup_var(var_ref)
                    elif isinstance(var_ref, ir.Literal):
                        # Case: literal value from `cast` relation, e.g. `decimal(0)`
                        vars.append(sql.VarRef(self._convert_value(var_ref.value), alias=alias))
                    else:
                        # Example: We may have `decimal(0)` in QB which turns in IR into:
                        #   (cast(Decimal128, 0, vDecimal128) and decimal128(vDecimal128, res_3))
                        #   and we need to make it `0` in SQL.
                        var_ref = var_ref.name if isinstance(var_ref, ir.Var) else str(var_ref)
                        vars.append(sql.VarRef(var_ref, alias=alias))
                elif task:
                    if isinstance(task, ir.Construct):
                        # Generate constructions like hash(`x`, `y`, TABLE_ALIAS.COLUMN_NAME) as `alias`
                        vars.append(sql.VarRef(handle_construct(task), alias=alias))
                    elif isinstance(task, ir.Aggregate):
                        result_arg = task.projection[-1] if task.aggregation == builtins.count else task.args[0]
                        result_arg = resolve_builtin_var(result_arg)
                        ref = reference(result_arg) if isinstance(result_arg, ir.Var) else str(result_arg)
                        vars.append(sql.VarRef(ref, alias=alias))
                    elif isinstance(task, ir.Union):
                        # Handle `COALESCE` of all lookups of this var from the union
                        lookups = self._extract_all_lookups_from_union(task)
                        elements = []

                        for lu in lookups:
                            if any(isinstance(arg, ir.Var) and arg == var for arg in lu.args):
                                column_name = self._var_name(lu.relation.id, var_column[var, lu])
                                elements.append(f"{sql_vars[lu]}.{column_name}")

                        expr = "COALESCE(" + ", ".join(elements) + ")"
                        vars.append(sql.VarRef(expr, alias=alias))
            else:
                # TODO - abusing even more here, because var is a value!
                value = self._convert_value(var, False)
                vars.append(sql.VarRef(str(value), alias=alias))
        return not_null_vars, vars

    def _generate_select_nots(self, nots: Optional[list[ir.Not]], var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]],
                              sql_vars: dict[ir.Lookup, str], var_column:dict[Tuple[ir.Var, ir.Lookup], ir.Field],
                              index: int) -> tuple[list[sql.NotExists], int]:
        not_exists = []
        if nots:
            for not_expr in nots:
                unions = []
                inner_nots = []
                constructs = []
                if isinstance(not_expr.task, ir.Lookup):
                    all_lookups = [not_expr.task]
                else:
                    logical = cast(ir.Logical, not_expr.task)
                    all_lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
                    logicals = cast(list[ir.Logical], filter_by_type(logical.body, ir.Logical))
                    inner_nots = cast(list[ir.Not], filter_by_type(logical.body, ir.Not))
                    unions = cast(list[ir.Union], filter_by_type(logical.body, ir.Union))
                    constructs = cast(list[ir.Construct], filter_by_type(logical.body, ir.Construct))

                    # Some of the lookup relations we wrap into logical and we need to get them out for the SQL compilation.
                    #    For example QB `decimal(0)` in IR will look like this:
                    #        Logical ^[res]
                    #           Exists(vDecimal128)
                    #               Logical
                    #                   cast(Decimal128, 0, vDecimal128)
                    #                   decimal128(vDecimal128, res)
                    if logicals:
                        unions = self._extract_all_of_type_from_logicals(logicals, ir.Union) + unions
                        all_lookups = self._extract_all_of_type_from_logicals(logicals, ir.Lookup) + all_lookups

                union_lookups: dict[ir.Union, OrderedSet[ir.Lookup]] = self._extract_all_lookups_per_union(unions)
                all_lookups.extend(list(chain.from_iterable(union_lookups.values())))

                lookups = OrderedSet.from_iterable(t for t in all_lookups if not builtins.is_builtin(t.relation))
                froms, wheres, not_sql_vars, not_var_column, not_var_lookups = self._extract_lookups_metadata(lookups, index)
                index += len(not_sql_vars)

                all_sql_vars = {**sql_vars, **not_sql_vars}
                all_var_column = {**var_column, **not_var_column}
                all_var_lookups = {**var_lookups, **not_var_lookups}

                var_to_construct = {c.id_var: c for c in constructs} if constructs else {}
                builtin_lookups = OrderedSet.from_iterable(t for t in all_lookups if builtins.is_builtin(t.relation))
                builtin_vars, builtin_wheres = self._resolve_builtins(builtin_lookups, all_var_lookups, all_var_column,
                                                                      all_sql_vars, var_to_construct)
                wheres.extend(builtin_wheres)

                # We need to join the not exists select with the outside select query context
                for arg, lookup_set in not_var_lookups.items():
                    if len(lookup_set) > 0:
                        lu = lookup_set[0]
                        column = not_var_column[cast(ir.Var, arg), lu]
                        column_name = self._var_name(lu.relation.id, column)
                        lhs = f"{not_sql_vars[lu]}.{column_name}"

                        # lookup the same var from the outside context to make the join
                        matching_lookup = next(
                            (lookup for (var, lookup) in var_column if var == arg),
                            None
                        )

                        if matching_lookup is not None:
                            matching_column = var_column[(arg, matching_lookup)]
                            matching_column_name = self._var_name(matching_lookup.relation.id, matching_column)
                            rhs = f"{sql_vars[matching_lookup]}.{matching_column_name}"
                            wheres.append(sql.Terminal(f"{lhs} = {rhs}"))

                wheres.extend(self._generate_where_clauses(not_var_lookups, not_var_column, not_sql_vars, union_lookups))

                inner_not_exists, index = self._generate_select_nots(inner_nots, not_var_lookups, not_sql_vars, not_var_column, index)
                wheres.extend(inner_not_exists)

                where = self._process_wheres_clauses(wheres)
                not_exists.append(sql.NotExists(sql.Select(False, [1], froms, where)))

        return not_exists, index

    def _extract_all_of_type_from_logical(self, task: ir.Logical, target_type: type) -> list:
        """Recursively extract all instances of `target_type` from a Logical task."""
        return self._extract_all_of_type_from_logicals([task], target_type)

    def _extract_all_of_type_from_logicals(self, logicals: list[ir.Logical], target_type: type) -> list:
        """Recursively extract all instances of `target_type` from a list of Logical tasks."""
        result = ordered_set()

        def visit(logical: ir.Logical):
            for expr in logical.body:
                if isinstance(expr, ir.Logical):
                    visit(expr)
                elif isinstance(expr, target_type):
                    result.add(expr)

        for logical in logicals or []:
            visit(logical)

        return result.list if result.list else []

    def _extract_all_lookups_per_union(self, unions: Optional[list[ir.Union]]) -> dict[ir.Union, OrderedSet[ir.Lookup]]:
        return {
            union: self._extract_all_lookups_from_union(union)
            for union in unions or []
        }

    def _extract_all_lookups_from_union(self, union: ir.Union) -> OrderedSet[ir.Lookup]:
        lookups: OrderedSet[ir.Lookup] = OrderedSet()
        for task in union.tasks:
            if isinstance(task, ir.Logical):
                lookups.update(self._extract_all_of_type_from_logicals([task], ir.Lookup))
            elif isinstance(task, ir.Lookup):
                lookups.add(cast(ir.Lookup, task))
        return lookups

    def _extract_all_not_null_vars_from_nots(self, nots: Optional[list[ir.Not]]) -> set[ir.Var]:
        vars: set[ir.Var] = set()
        null_vars: set[ir.Var] = set()

        def visit(task):
            if isinstance(task, ir.Not):
                visit(task.task)
            elif isinstance(task, ir.Logical):
                for var in task.hoisted:
                    if isinstance(var, ir.Var):
                        vars.add(var)
                    elif isinstance(var, ir.Default):
                        (vars if var.value is not None else null_vars).add(var.var)
                for subtask in task.body:
                    visit(subtask)
            elif isinstance(task, ir.Lookup):
                vars.update(arg for arg in task.args if isinstance(arg, ir.Var))

        for not_task in nots or []:
            visit(not_task)

        return vars - null_vars

    def _var_to_expr(self, var, reference, resolve_builtin_var, var_to_construct: dict[ir.Var, ir.Construct]):
        """
        Convert a variable to an expression string.
        """
        if isinstance(var, ir.Var) and var in var_to_construct:
            return self._resolve_construct_var(reference, resolve_builtin_var, var_to_construct[var])
        resolved = resolve_builtin_var(var)
        return reference(resolved) if isinstance(resolved, ir.Var) else str(resolved)

    def _get_alias(self, key, arg, var_to_construct, var_to_union):
        if not isinstance(arg, ir.Var):
            return key, arg

        var_task = var_to_construct.get(arg) or var_to_union.get(arg)
        return (key, arg, var_task) if var_task else (key, arg)

    def _get_tuples(self, logical: ir.Logical, u: ir.Update):
        """
        Get a list of tuples to perform this update.

        This function traverses the update args, assuming they contain only static values or
        variables bound to a construct task, and generates a list of tuples to insert. There
        may be multiple tuples because arguments can be lists of values bound to a field
        whose role is multi.
        """
        # TODO - this only works if the variable is bound to a Construct task, we need a more general approach.

        def find_construct(var):
            for stmt in logical.body:
                if isinstance(stmt, ir.Construct) and stmt.id_var == var:
                    return stmt
            return None

        def resolve_value(arg):
            if isinstance(arg, ir.Var):
                construct = find_construct(arg)
                if not construct:
                    return self._convert_value(arg)

                resolved = []
                for val in construct.values:
                    if isinstance(val, ir.Var):
                        inner_construct = find_construct(val)
                        if inner_construct:
                            nested = [self._convert_value(x, True) for x in inner_construct.values]
                            resolved.append(f"hash({', '.join(nested)})")
                        else:
                            resolved.append(self._convert_value(val, True))
                    else:
                        resolved.append(self._convert_value(val, True))

                return f"hash({', '.join(resolved)})"
            elif isinstance(arg, FrozenOrderedSet):
                return frozen(*[self._convert_value(v) for v in arg])
            else:
                return self._convert_value(arg)

        values = [resolve_value(a) for a in u.args]
        return self._product(values)

    def _product(self, values):
        """ Compute a cartesian product of values when the value is a FrozenOrderedSet. """
        # TODO - some pass needs to check that this is correct, i.e. that we are using a
        # FrozenOrderedSet only if the field is of role multi.
        tuples = [[]]
        for value in values:
            if isinstance(value, FrozenOrderedSet):
                tuples = [prev + [element] for prev in tuples for element in value]
            else:
                tuples = [prev + [value] for prev in tuples]
        return [tuple(t) for t in tuples]

    def _convert_value(self, v, quote_numbers:bool=False) -> str:
        """ Convert the literal value in v to a SQL value."""
        if isinstance(v, str):
            return f"'{v}'"
        if isinstance(v, PyDecimal):
            return str(v)
        if isinstance(v, ir.ScalarType):
            return f"'{v.name}'"
        if isinstance(v, ir.Literal):
            return self._convert_value(v.value, quote_numbers)
        if isinstance(v, float):
            if math.isnan(v):
                return "cast('NaN' as DOUBLE)"
            elif v == float("inf"):
                return "cast('Infinity' as DOUBLE)"
            elif v == float("-inf"):
                return "cast('-Infinity' as DOUBLE)"
            return str(v) if not quote_numbers else f"'{v}'"
        return v if not quote_numbers else f"'{v}'"

    COMMON_CONVERSION = {
        Hash: "DECIMAL(38, 0)",
        String: "TEXT",
        Number: "DOUBLE",
        Decimal64: "DECIMAL(19, 6)",
        Decimal128: "DECIMAL(38, 10)",
        Bool: "BOOLEAN",
        Date: "DATE",
        DateTime: "DATETIME",
        Float: "FLOAT(53)",
    }
    SNOWFLAKE_OVERRIDES = {
        Int64: "NUMBER(19, 0)",
        Int128: "NUMBER(38, 0)",
    }
    DUCKDB_OVERRIDES = {
        Int64: "BIGINT",
        Int128: "HUGEINT",
    }
    SF_BUILTIN_CONVERSION = {**COMMON_CONVERSION, **SNOWFLAKE_OVERRIDES}
    DUCKDB_BUILTIN_CONVERSION = {**COMMON_CONVERSION, **DUCKDB_OVERRIDES}
    def _convert_type(self, t: ir.Type, is_duck_db:bool) -> str:
        """ Convert the type t into the equivalent SQL type."""
        # entities become DECIMAL(38, 0)
        if not types.is_builtin(t) and not types.is_value_type(t):
            return "DECIMAL(38, 0)"

        # convert known builtins
        base_type = typer.to_base_primitive(t)
        if isinstance(base_type, ir.ScalarType):
            if is_duck_db and base_type in self.DUCKDB_BUILTIN_CONVERSION:
                return self.DUCKDB_BUILTIN_CONVERSION[base_type]
            elif base_type in self.SF_BUILTIN_CONVERSION:
                return self.SF_BUILTIN_CONVERSION[base_type]
        raise Exception(f"Unknown built-in type: {t}")

    def _get_relations(self, model: ir.Model, query_compilation: bool) -> list[ir.Relation]:
        # Filter only relations that require table creation
        relations = [
            r for r in model.relations
            if self._is_table_creation_required(r)
        ]

        # Optionally exclude read-only tables
        if query_compilation:
            rw = ReadWriteVisitor()
            model.accept(rw)
            writable = rw.writes(cast(ir.Logical, model.root))
            relations = [r for r in relations if r in writable]

        return relations

    def _is_table_creation_required(self, r: ir.Relation) -> bool:
        """
        Determine whether the given relation should result in a SQL table creation.

        Skips creation for:
        - Built-in relations or annotations
        - CDC relations
        - Boxed types or special "rank" name
        - Relations with unresolved field types (types.Any)
        - ValueType population relations
        """
        if (
            builtins.is_builtin(r) or
            builtins.is_annotation(r) or
            from_cdc_annotation in r.annotations or
            r.name == "rank"
        ):
            return False

        if any(relation_field.type == types.Any for relation_field in r.fields):
            if not r.overloads:
                raise ValueError(f"Relation '{r.name}' has unresolved field types (`types.Any`) and no overloads.")
            return False

        return not self._is_value_type_population_relation(r)

    @staticmethod
    def _is_value_type_population_relation(r: ir.Relation) -> bool:
        """
        Check if the relation is a ValueType population relation:
        - Has exactly one field
        - Field type is a value type
        - Annotated with concept_relation_annotation
        """
        if not r.fields or len(r.fields) != 1:
            return False
        return types.is_value_type(r.fields[0].type) and concept_relation_annotation in r.annotations

    def _relation_name(self, relation: ir.Relation):
        if helpers.is_external(relation) or helpers.builtins.is_builtin(relation):
            return relation.name
        return self.relation_name_cache.get_name(relation.id, relation.name, helpers.relation_name_prefix(relation))

    def _register_external_relations(self, model: ir.Model):
        # force all external relations to get a name in the cache, so that internal relations
        # cannot use those names in _relation_name
        for r in model.relations:
            if helpers.is_external(r):
                self.relation_name_cache.get_name(r.id, r.name)

    def _var_name(self, relation_id: int, arg: Union[ir.Var, ir.Field]):
        name = self.relation_arg_name_cache.get_name((relation_id, arg.id), arg.name)
        return f'"{name}"' if name.lower() == "any" else name

    def _register_relation_args(self, relations: list[ir.Relation]):
        """
        Register all relation arguments in the cache to ensure they have unique names.
        This is necessary for SQL compilation to avoid name collisions.
        """
        self.relation_arg_name_cache = NameCache()
        for r in relations:
            for rel_field in r.fields:
                self.relation_arg_name_cache.get_name((r.id, rel_field.id), rel_field.name)

    def _sort_builtin_lookups(self, lookups: list[ir.Lookup], output_vars: set[ir.Var]) -> list[ir.Lookup]:
        # Process lookups with output vars at last because they depend on other builtin lookups.
        lookups_with_output_vars = [lookup for lookup in lookups if lookup.relation.name == builtins.eq.name
                                    and any(arg in output_vars for arg in lookup.args)]
        other_lookups = [lookup for lookup in lookups if lookup not in lookups_with_output_vars]

        sorted_lookups = topological_sort(other_lookups, self._build_builtin_lookups_dependencies(other_lookups))

        return sorted_lookups + lookups_with_output_vars

    @staticmethod
    def _build_builtin_lookups_dependencies(lookups: list[ir.Lookup]) -> list[Tuple[ir.Lookup, ir.Lookup]]:
        """
        Builds dependency edges for topological_sort:
        1. A lookup whose last argument is used non-terminally in another must come first.
        2. Terminal comparisons (neq, gt, lt, gte, lte) come last.
        3. Conditionals (starts_with, contains, etc.) come after basic lookups but before terminals.
        4. eq with only constants comes first.
        5. eq with two vars must wait until one of them is grounded.
        """

        edges = []
        arg_usages = defaultdict(list)  # arg -> List[(lookup, position)]

        terminal_relations = {
            builtins.neq.name, builtins.gt.name, builtins.lt.name, builtins.gte.name, builtins.lte.name
        }

        conditional_relations = {
            builtins.starts_with.name, builtins.ends_with.name, builtins.contains.name, builtins.like_match.name
        }

        # Step 1: Collect argument usage positions
        for lookup in lookups:
            for idx, arg in enumerate(lookup.args):
                arg_usages[arg].append((lookup, idx))

        # Step 2: Add edges based on lookup semantics
        for lookup in lookups:
            relation_name = lookup.relation.name
            args = lookup.args

            # Rule 2: Terminal relations depend on everything else
            if relation_name in terminal_relations:
                for other in lookups:
                    if other is not lookup:
                        edges.append((other, lookup))
                continue  # skip rest of rules for terminal lookups

            # Rule 3: Conditional relations go before terminals, but after others
            if relation_name in conditional_relations:
                for other in lookups:
                    if other is not lookup:
                        other_name = other.relation.name
                        if other_name not in terminal_relations and other_name not in conditional_relations:
                            edges.append((other, lookup))  # only non-conditional, non-terminal
                continue

            if relation_name == builtins.eq.name:
                var_args = [arg for arg in args if isinstance(arg, ir.Var)]

                # Rule 4: eq with only constants comes first
                if len(var_args) == 1:
                    # This lookup defines a var — should come before any that use this var non-terminally
                    grounded_var = var_args[0]
                    for other_lookup, pos in arg_usages[grounded_var]:
                        if other_lookup is not lookup:
                            if pos != len(other_lookup.args) - 1:
                                edges.append((lookup, other_lookup))
                    continue  # skip adding other edges among terminal assignments like a=2, b=2

                # Rule 5: eq with two vars must wait until one of them is grounded
                elif len(var_args) == 2:
                    # eq(x, y): both are vars — lookup must come after those grounding either var
                    for var in var_args:
                        for other_lookup, pos in arg_usages[var]:
                            if other_lookup is not lookup:
                                if other_lookup.args[-1] == var:
                                    edges.append((other_lookup, lookup))
                    continue

            # Rule 1: last argument used elsewhere non-terminally — must go first
            last_arg = args[-1]
            for other_lookup, pos in arg_usages.get(last_arg, []):
                if other_lookup is not lookup and pos != len(other_lookup.args) - 1:
                    edges.append((lookup, other_lookup))

        return edges


    # TODO: need to check if inserts may depend on any view and if so then sort them together.
    def _sort_dependencies(self, statements: list[sql.Node]) -> list[sql.Node]:
        """
            Sorts SQL statements to ensure proper execution order:
            1. CREATE TABLE statements
            2. INSERT statements (topologically sorted by dependencies)
            3. UPDATE statements
            3. Other statements except SELECT queries (e.g., CREATE VIEW, etc.)
            4. SELECT queries
        """
        create_tables = []
        inserts: dict[str, list[sql.Insert]] = defaultdict(list)
        updates = []
        miscellaneous_statements = []
        selects = []

        for statement in statements:
            if isinstance(statement, sql.CreateTable):
                create_tables.append(statement)
            elif isinstance(statement, sql.Insert):
                inserts[statement.table].append(statement)
            elif isinstance(statement, sql.Update):
                updates.append(statement)
            elif isinstance(statement, sql.Select):
                selects.append(statement)
            else:
                miscellaneous_statements.append(statement)

        sorted_inserts = self._sort_inserts_dependency_graph(inserts)

        return create_tables + sorted_inserts + updates + miscellaneous_statements + selects

    @staticmethod
    def _sort_inserts_dependency_graph(insert_statements: dict[str, list[sql.Insert]]) -> list[sql.Insert]:
        """ Topologic sort INSERT statements based on dependencies in their SELECT FROM clauses. """
        edges = ordered_set()
        nodes = OrderedSet.from_iterable(insert_statements.keys())

        def extract_dependencies(select: Optional[sql.Select], target_table: str):
            """Recursively extract dependency edges from FROM, JOIN, and WHERE clauses."""
            if not select:
                return

            def register_dependency(source_table: str):
                edges.add((source_table, target_table))
                nodes.add(source_table)

            # Process FROM clause
            if select.froms:
                if isinstance(select.froms, sql.Select):  # Single sub-select
                    extract_dependencies(select.froms, target_table)
                else:
                    for from_clause in select.froms:
                        register_dependency(from_clause.table)

            # Process JOIN clause
            if select.joins:
                for join in select.joins:
                    register_dependency(join.table)

            # Process WHERE clause recursively
            def _extract_from_expr(expr: sql.Expr):
                if isinstance(expr, sql.NotExists):
                    extract_dependencies(expr.expr, target_table)
                elif isinstance(expr, (sql.And, sql.Or)):
                    for sub_expr in expr.expr:
                        _extract_from_expr(sub_expr)

            if select.where:
                _extract_from_expr(select.where.expression)

        for target_table, inserts in insert_statements.items():
            for insert in inserts:
                extract_dependencies(insert.select, target_table)

        sorted_tables = topological_sort(list(nodes), list(edges))

        sorted_inserts = []
        for table in sorted_tables:
            if table in insert_statements:
                sorted_inserts.extend(insert_statements.get(table, []))

        return sorted_inserts
