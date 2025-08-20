from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, factory as f, visitor
from relationalai.early_access.metamodel.typer import Checker, InferTypes
from relationalai.early_access.metamodel import helpers, types
from relationalai.early_access.metamodel.rewrite import Splinter, ExtractNestedLogicals
from relationalai.early_access.metamodel.util import FrozenOrderedSet

from relationalai.early_access.metamodel.rewrite import Flatten
# TODO: Move this into metamodel.rewrite
from relationalai.early_access.rel.rewrite import QuantifyVars, CDC

from relationalai.early_access.lqp.utils import is_constant, output_names

import datetime
from decimal import Decimal as PyDecimal
from typing import cast, List, Sequence, Tuple, Union

def lqp_passes() -> list[Pass]:
    return [
        Checker(),
        ExtractNestedLogicals(), # before InferTypes to avoid extracting casts
        InferTypes(),
        CDC(),
        # Broken
        # ExtractCommon(),
        Flatten(),
        Splinter(), # Splits multi-headed rules into multiple rules
        QuantifyVars(), # Adds missing existentials
        UnifyDefinitions(),
        EliminateData(),  # Turns Data nodes into ordinary relations.
        EliminateValueTypeConstants(),
        DeduplicateVars(),  # Deduplicates vars in Updates and Outputs.
    ]

class UnifyDefinitions(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        multidef_relations = self.get_multidef_relations(model)
        for relation in multidef_relations:
            model = self.rename_multidef(model, relation)
        return model

    def get_multidef_relations(self, model: ir.Model) -> set[ir.Relation]:
        seen = set()
        result = set()
        root = cast(ir.Logical, model.root)
        for task in root.body:
            task = cast(ir.Logical, task)
            for subtask in task.body:
                if isinstance(subtask, ir.Update):
                    assert subtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subtask.relation
                    if name.id in seen:
                        result.add(name)
                    seen.add(name.id)
        return result

    def rename_multidef(self, model: ir.Model, relation: ir.Relation) -> ir.Model:
        root = cast(ir.Logical, model.root)

        new_subtasks = []
        new_relations = []
        generated_relation_names = {}
        total_ct = 0

        # Rename occurrences of the relation in the model
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks: list[ir.Task] = []
            for subsubtask in subtask.body:
                if isinstance(subsubtask, ir.Update):
                    assert subsubtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subsubtask.relation
                    if name.id == relation.id:
                        total_ct += 1
                        # TODO: this needs to be unique btw (gensym)
                        new_name = f"{relation.name}_{total_ct}"

                        # Check if we already generated this relation name. If we did, just
                        # reuse it, otherwise we end up with undefined relation IDs.
                        if new_name in generated_relation_names:
                            new_relation = generated_relation_names[new_name]
                        else:
                            new_relation = ir.Relation(
                                new_name,
                                name.fields,
                                name.requires,
                            )
                            new_relations.append(new_relation)
                            generated_relation_names[new_name] = new_relation

                        new_subsubtask = ir.Update(
                            subsubtask.engine,
                            new_relation,
                            subsubtask.args,
                            subsubtask.effect,
                        )
                        new_subsubtasks.append(new_subsubtask)
                    else:
                        new_subsubtasks.append(subsubtask)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                subtask.engine,
                subtask.hoisted,
                tuple(new_subsubtasks),
            )
            new_subtasks.append(new_subtask)

        assert total_ct > 0, f"should have found at least one definition for {relation.name}"

        args = []
        for field in relation.fields:
            args.append(ir.Var(field.type, field.name))

        # Also add the new definition, using the existing relation
        new_update = ir.Update(
            root.engine,
            relation,
            tuple(args),
            ir.Effect.derive,
        )

        logical_tasks = []
        lookups = []
        for new_relation in new_relations:
            new_lookup = ir.Lookup(
                root.engine,
                new_relation,
                tuple(args),
            )
            lookups.append(new_lookup)

        disj = ir.Union(
            root.engine,
            tuple(),
            tuple(lookups),
        )
        logical_tasks.append(disj)
        logical_tasks.append(new_update)
        new_logical = ir.Logical(
            root.engine,
            root.hoisted,
            tuple(logical_tasks),
        )
        new_subtasks.append(new_logical)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations | new_relations,
            model.types,
            new_root,
        )
        return model

# Eliminate value type constants to constructors that can be represented in the protos.
class EliminateValueTypeConstants(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.RewriteBadLiterals()
        return r.walk(model)

    # Rewrites 'bad' python literals (datetime, date, decimal), or metamodel.Literal
    # wrappers for those types, into lookups of constructors for the appropriate LQP type.
    class RewriteBadLiterals(visitor.Rewriter):
        def rewrite_bad_literals(self, args):
            vars_to_existify = []
            new_conjs = []
            new_args = []

            for arg in args:
                if is_constant(arg, datetime.datetime):
                    if isinstance(arg, ir.Literal):
                        arg = arg.value
                    new_var = f.var("dt_var", types.DateTime)
                    new_args.append(new_var)
                    vars_to_existify.append(new_var)

                    year = arg.year
                    month = arg.month
                    day = arg.day
                    hour = arg.hour
                    minute = arg.minute
                    second = arg.second

                    lookup = f.lookup(
                        rel_builtins.construct_datetime_ms_tz,
                        tuple([
                            f.literal(year, type=types.Int64),
                            f.literal(month, type=types.Int64),
                            f.literal(day, type=types.Int64),
                            f.literal(hour, type=types.Int64),
                            f.literal(minute, type=types.Int64),
                            f.literal(second, type=types.Int64),
                            f.literal(0, type=types.Int64),
                            f.literal("UTC", type=types.String),
                            new_var,
                        ])
                    )
                    new_conjs.append(lookup)
                elif is_constant(arg, datetime.date):
                    if isinstance(arg, ir.Literal):
                        arg = arg.value
                    new_var = f.var("dt_var", types.Date)
                    new_args.append(new_var)
                    vars_to_existify.append(new_var)

                    year = arg.year
                    month = arg.month
                    day = arg.day

                    lookup = f.lookup(
                        rel_builtins.construct_date,
                        tuple([
                            f.literal(year, type=types.Int64),
                            f.literal(month, type=types.Int64),
                            f.literal(day, type=types.Int64),
                            new_var,
                        ])
                    )
                    new_conjs.append(lookup)
                elif is_constant(arg, PyDecimal):
                    if isinstance(arg, ir.Literal):
                        t = arg.type
                        arg = arg.value
                    else:
                        t = types.Decimal128
                    new_var = f.var("dec_var", t)
                    new_args.append(new_var)
                    vars_to_existify.append(new_var)

                    if t == types.Decimal64:
                        lookup = f.lookup(
                            rel_builtins.parse_decimal,
                            tuple([
                                f.literal(64, types.Symbol),
                                f.literal(6, types.Symbol),
                                f.literal(str(arg)),
                                new_var
                            ]),
                        )
                    elif t == types.Decimal128:
                        lookup = f.lookup(
                            rel_builtins.parse_decimal,
                            tuple([
                                f.literal(128, types.Symbol),
                                f.literal(10, types.Symbol),
                                f.literal(str(arg)),
                                new_var
                            ]),
                        )
                    else:
                        raise ValueError(f"Unsupported decimal type: {t}")
                    new_conjs.append(lookup)
                else:
                    new_args.append(arg)

            return new_args, vars_to_existify, new_conjs

        def handle_lookup(self, node: ir.Lookup, parent: ir.Node) -> Union[ir.Lookup, ir.Exists]:
            args = node.args
            new_args, vars_to_existify, new_conjs = self.rewrite_bad_literals(args)

            if len(vars_to_existify) == 0:
                return node

            new_lookup = f.lookup(
                node.relation,
                tuple(new_args),
            )
            new_conjs.append(new_lookup)

            result = f.exists(
                vars_to_existify,
                f.logical(tuple(new_conjs)),
            )

            return result

        def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node) -> Union[ir.Aggregate, ir.Exists]:
            args = node.args
            new_args, vars_to_existify, new_conjs = self.rewrite_bad_literals(args)

            if len(vars_to_existify) == 0:
                return node

            new_aggregate = node.reconstruct(args=tuple(new_args))
            new_conjs.append(new_aggregate)

            result = f.exists(
                vars_to_existify,
                f.logical(tuple(new_conjs)),
            )

            return result

        def handle_output(self, node: ir.Output, parent: ir.Node) -> Union[ir.Output, ir.Logical]:
            args = helpers.output_values(node.aliases)
            new_args, vars_to_existify, new_conjs = self.rewrite_bad_literals(args)

            if len(vars_to_existify) == 0:
                return node

            alias_names = output_names(node.aliases)
            new_output = node.reconstruct(
                aliases=FrozenOrderedSet(list(zip(alias_names, new_args))),
            )
            new_conjs.append(new_output)

            return f.logical(new_conjs)

        def handle_update(self, node: ir.Update, parent: ir.Node) -> Union[ir.Update, ir.Logical]:
            args = node.args
            new_args, vars_to_existify, new_conjs = self.rewrite_bad_literals(args)

            if len(vars_to_existify) == 0:
                return node

            new_update = node.reconstruct(args=tuple(new_args))
            new_conjs.append(new_update)
            return f.logical(new_conjs)

        def handle_construct(self, node: ir.Construct, parent: ir.Node) -> Union[ir.Construct, ir.Exists]:
            values = node.values
            new_values, vars_to_existify, new_conjs = self.rewrite_bad_literals(values)

            if len(vars_to_existify) == 0:
                return node

            new_construct = node.reconstruct(values=tuple(new_values))
            new_conjs.append(new_construct)
            return f.exists(
                vars_to_existify,
                f.logical(tuple(new_conjs)),
            )

# Creates intermediary relations for all Data nodes and replaces said Data nodes
# with a Lookup into these created relations.
class EliminateData(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.DataRewriter()
        return r.walk(model)

    # Does the actual work.
    class DataRewriter(visitor.Rewriter):
        new_relations: list[ir.Relation]
        new_updates: list[ir.Logical]
        # Counter for naming new relations.
        # It must be that new_count == len new_updates == len new_relations.
        new_count: int

        def __init__(self):
            self.new_relations = []
            self.new_updates = []
            self.new_count = 0
            super().__init__()

        # Create a new intermediary relation representing the Data (and pop it in
        # new_updates/new_relations) and replace this Data with a Lookup of said
        # intermediary.
        def handle_data(self, node: ir.Data, parent: ir.Node) -> ir.Lookup:
            self.new_count += 1
            intermediary_name = f"formerly_Data_{self.new_count}"

            intermediary_relation = f.relation(
                intermediary_name,
                [f.field(v.name, v.type) for v in node.vars]
            )
            self.new_relations.append(intermediary_relation)

            intermediary_update = f.logical([
                # For each row (union), equate values and their variable (logical).
                f.union(
                    [
                        f.logical(
                            [
                                f.lookup(rel_builtins.eq, [val, var])
                                for (val, var) in zip(row, node.vars)
                            ],
                            hoisted = node.vars,
                        )
                        for row in node
                    ],
                    hoisted = node.vars,
                ),
                # And pop it back into the relation.
                f.update(intermediary_relation, node.vars, ir.Effect.derive),
            ])
            self.new_updates.append(intermediary_update)

            replacement_lookup = f.lookup(intermediary_relation, node.vars)

            return replacement_lookup

        # Walks the model for the handle_data work then updates the model with
        # the new state.
        def handle_model(self, model: ir.Model, parent: None):
            walked_model = super().handle_model(model, parent)
            assert len(self.new_relations) == len(self.new_updates) and self.new_count == len(self.new_relations)

            # This is okay because its LQP.
            assert isinstance(walked_model.root, ir.Logical)
            root_logical = cast(ir.Logical, walked_model.root)

            # We may need to add the new intermediaries from handle_data to the model.
            if self.new_count  == 0:
                return model
            else:
                return ir.Model(
                    walked_model.engines,
                    walked_model.relations | self.new_relations,
                    walked_model.types,
                    ir.Logical(
                        root_logical.engine,
                        root_logical.hoisted,
                        root_logical.body + tuple(self.new_updates),
                        root_logical.annotations,
                    ),
                    walked_model.annotations,
                )

# Deduplicate Vars in Updates and Outputs.
class DeduplicateVars(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        r = self.VarDeduplicator()
        return r.walk(model)

    # Return 1) a new list of Values with no duplicates (at the object level) and
    # 2) equalities between any original Value and a deduplicated Value.
    @staticmethod
    def dedup_values(vals: Sequence[ir.Value]) -> Tuple[List[ir.Value], List[ir.Lookup]]:
        # If a var is seen more than once, it is a duplicate and we will create
        # a new Var and equate it with the seen one.
        seen_vars = set()

        new_vals = []
        eqs = []

        for i, val in enumerate(vals):
            # Duplicates can only occur within Vars.
            # TODO: we don't know for sure if these are the only relevant cases.
            if isinstance(val, ir.Default) or isinstance(val, ir.Var):
                var = val if isinstance(val, ir.Var) else val.var
                if var in seen_vars:
                    new_var = ir.Var(var.type, var.name + "_dup_" + str(i))
                    new_val = new_var if isinstance(val, ir.Var) else ir.Default(new_var, val.value)
                    new_vals.append(new_val)
                    eqs.append(f.lookup(rel_builtins.eq, [new_var, var]))
                else:
                    seen_vars.add(var)
                    new_vals.append(val)
            else:
                # No possibility of problematic duplication.
                new_vals.append(val)

        return new_vals, eqs

    # Returns a reconstructed output with no duplicate variable objects
    # (dedup_values) and now necessary equalities between any two previously
    # duplicate variables.
    @staticmethod
    def dedup_output(output: ir.Output) -> List[Union[ir.Output, ir.Lookup]]:
        vals = helpers.output_values(output.aliases)
        deduped_vals, req_lookups = DeduplicateVars.dedup_values(vals)
        # Need the names so we can recombine.
        alias_names = output_names(output.aliases)
        new_output = output.reconstruct(
            output.engine,
            FrozenOrderedSet(list(zip(alias_names, deduped_vals))),
            output.keys,
            output.annotations,
        )
        return [new_output] + req_lookups

    # Returns a reconstructed update with no duplicate variable objects
    # (dedup_values) and now necessary equalities between any two previously
    # duplicate variables.
    @staticmethod
    def dedup_update(update: ir.Update) -> List[Union[ir.Update, ir.Lookup]]:
        deduped_vals, req_lookups = DeduplicateVars.dedup_values(update.args)
        new_update = update.reconstruct(
            update.engine,
            update.relation,
            tuple(deduped_vals),
            update.effect,
            update.annotations,
        )
        return [new_update] + req_lookups

    # Does the actual work.
    class VarDeduplicator(visitor.Rewriter):
        def __init__(self):
            super().__init__()

        # We implement handle_logical instead of handle_update/handle_output
        # because in addition to modifying said update/output we require new
        # lookups (equality between original and deduplicated variables).
        def handle_logical(self, node: ir.Logical, parent: ir.Node):
            # In order to recurse over subtasks.
            node = super().handle_logical(node, parent)

            new_body = []
            for subtask in node.body:
                if isinstance(subtask, ir.Output):
                    new_body.extend(DeduplicateVars.dedup_output(subtask))
                elif isinstance(subtask, ir.Update):
                    new_body.extend(DeduplicateVars.dedup_update(subtask))
                else:
                    new_body.append(subtask)

            return node.reconstruct(
                node.engine,
                node.hoisted,
                tuple(new_body),
                node.annotations
            )
