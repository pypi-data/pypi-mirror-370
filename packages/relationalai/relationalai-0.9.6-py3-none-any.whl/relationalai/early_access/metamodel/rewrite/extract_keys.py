from __future__ import annotations

from relationalai.early_access.metamodel import ir
from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel.visitor import Visitor, Rewriter
from relationalai.early_access.metamodel.util import OrderedSet
from relationalai.early_access.metamodel import helpers, factory as f, types, builtins
from typing import Optional, Any, Iterable

# Given an Output with a group of keys (some of them potentially null),
# * extract the lookups that bind (transitively) all the keys
# * generate all the valid combinations of keys being present or not
#   * first all keys are present,
#   * then we remove one key at a time,
#   * then we remove two keys at a time,and so on.
#   * the last combination is when all the *nullable* keys are missing.
# * each combination is using the keys to create a compound (hash) key
# * create a Match handling all the cases
# * any key lookup is removed from the original logicals,
#   and is moved at the same level as the Match
# * update the original Output to now use the compound key
#
# E.g., we go from
#
# Logical
#     Foo(foo)
#     rel1(foo, x)
#     Logical ^[v1=None]
#         rel2(foo, v1)
#     Logical ^[v2=None, k2=None]
#         rel3(foo, k2)
#         rel4(k2, v2)
#     Logical ^[v3=None, k3=None]
#         rel5(foo, y)
#         rel6(y, k3)
#         rel7(k3, v3)
#     output[foo, k2, k3](v1, v2, v3)
#
# to
#
# Logical
#     Logical ^[foo, k2=None, k3=None, compound_key]
#         Foo(foo)
#         rel1(foo, x)
#         Match ^[k2=None, k3=None]
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 rel5(foo, y)
#                 rel6(y, k3)
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 k3 = None
#             Logical ^[k2=None, k3=None]
#                 rel5(foo, y)
#                 rel6(y, k3)
#                 k2 = None
#             Logical ^[k2=None, k3=None]
#                 k2 = None
#                 k3 = None
#         construct(Hash, "Foo", foo, "Concept2", k2, "Concept3", k3, compound_key)
#     Logical ^[v1=None]
#         rel2(foo, v1)
#     Logical ^[v2=None, k2=None]
#         rel4(k2, v2)
#     Logical ^[v3=None, k3=None]
#         rel7(k3, v3)
#     output[compound_key](v1, v2, v3)

class ExtractKeys(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        visitor = IdentifyKeysVisitor()
        model.accept(visitor)
        return ExtractKeysRewriter(visitor).walk(model)

class ExtractInfo:
    def __init__(self, vars_to_extract: OrderedSet[ir.Var]):
        self.original_keys = vars_to_extract
        # the subsets of the original keys that are nullable or not.
        self.non_nullable_keys: OrderedSet[ir.Var] = OrderedSet()
        self.nullable_keys: OrderedSet[ir.Var] = OrderedSet()
        # lookup tasks that transitively bind all the key vars
        # e.g., if the key is Z, in foo(X, Y), bar(Y, Z), baz(Z, W)
        # we extract foo(X, Y), bar(Y, Z)
        self.key_lookups: list[ir.Task] = []
        # variables coming from concept lookups, that are not nullable
        # this includes lookups at the top-level, as well as inside logicals when
        # hoisted without a None default.
        self.non_nullable_vars: OrderedSet[ir.Var] = OrderedSet()

class IdentifyKeysVisitor(Visitor):
    def __init__(self):
        self.extract_info_for_logical: dict[ir.Logical, ExtractInfo] = {}
        self.curr_info = None

    def enter(self, node: ir.Node, parent: Optional[ir.Node]=None) -> Visitor:
        if isinstance(node, ir.Logical):
            outputs = [x for x in node.body if isinstance(x, ir.Output) and x.keys]
            if not outputs:
                return self
            assert len(outputs) == 1, "multiple outputs with keys in a logical"
            if not outputs[0].keys:
                return self

            # Logical with an output that has keys
            info = ExtractInfo(OrderedSet.from_iterable(outputs[0].keys))

            # the original keys and any intermediate vars needed to correctly bind the keys
            extended_keys:OrderedSet[ir.Var] = OrderedSet.from_iterable(outputs[0].keys)

            # first, collect all the top-level lookups
            top_level_lookups = []
            for task in node.body:
                if isinstance(task, ir.Lookup):
                    top_level_lookups.append(task)
            key_lookups = self.find_key_lookups_fixpoint(top_level_lookups, extended_keys)

            # then, deal with key lookups inside logicals (with hoisted defaults)
            for task in node.body:
                # top-level concept lookups identify variables that are not nullable
                if isinstance(task, ir.Lookup) and helpers.is_concept_lookup(task):
                    vars = helpers.vars(task.args)
                    if vars[0] not in info.non_nullable_vars:
                        info.non_nullable_vars.add(vars[0])

                if isinstance(task, ir.Logical):
                    for h in task.hoisted:
                        # hoisted vars without a default are not nullable
                        if isinstance(h, ir.Var):
                            info.non_nullable_vars.add(h)
                        elif isinstance(h, ir.Default):
                            # hoisted vars with a non-None default are not nullable
                            if h.value is not None:
                                info.non_nullable_vars.add(h.var)
                            elif h.var in info.original_keys and h.var not in info.non_nullable_vars:
                                info.nullable_keys.add(h.var)

                    current_lookups = self.find_key_lookups_fixpoint(task.body, extended_keys)
                    key_lookups.update(current_lookups)

            info.non_nullable_keys = info.original_keys - info.nullable_keys
            info.key_lookups = list(key_lookups)

            # we only need to transform the logical if there are nullable keys
            if info.nullable_keys:
                self.extract_info_for_logical[node] = info
                self.curr_info = info
        return self

    def leave(self, node: ir.Node, parent: Optional[ir.Node]=None) -> ir.Node:
        if not self.curr_info:
            return node

        if isinstance(node, ir.Aggregate):
            # we assume that variables appearing in aggregate group-by's are not nullable
            for v in node.group:
                if v in self.curr_info.nullable_keys:
                    self.curr_info.nullable_keys.remove(v)
        elif isinstance(node, ir.Logical) and node in self.extract_info_for_logical:
            # if the set of nullable keys became empty, we shouldn't attempt to transform the logical
            if not self.curr_info.nullable_keys:
                self.extract_info_for_logical.pop(node)
            self.curr_info = None

        return node

    def find_key_lookups_fixpoint(self, tasks:Iterable[ir.Task], keys:OrderedSet[ir.Var]):
        # lookups with a single argument correspond to concepts.
        # we should keep them ahead of the other lookups.
        concept_lookups = OrderedSet()
        # for lookups with multiple arguments, we start from those that have a key as the last
        # argument and move backwards. that's why each time we insert at the front of the list
        lookups = OrderedSet()

        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in tasks:
                if isinstance(task, ir.Lookup) and task not in lookups and task not in concept_lookups:
                    vars = helpers.vars(task.args)
                    if len(vars) == 1 and vars[0] in keys:
                        concept_lookups.add(task)
                        there_is_progress = True
                    elif len(vars) > 1 and all(v in keys for v in vars[1:]):
                        assert isinstance(vars[0], ir.Var)
                        keys.add(vars[0])
                        lookups.prepend(task)
                        there_is_progress = True

        return concept_lookups | lookups

class ExtractKeysRewriter(Rewriter):
    def __init__(self, visitor: IdentifyKeysVisitor):
        super().__init__()
        self.visitor = visitor

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None) -> ir.Logical:
        new_body = self.walk_list(node.body, node)

        # We are in a logical with an output at this level.
        if node in self.visitor.extract_info_for_logical:
            info = self.visitor.extract_info_for_logical[node]

            # update the key sets based on the identified non-nullable vars
            # remove nullable keys that were inferred to be non-nullable,
            # and add them to the non-nullable set
            non_null_nullable_keys = info.nullable_keys & info.non_nullable_vars
            info.non_nullable_keys.update(non_null_nullable_keys)
            info.nullable_keys = info.nullable_keys - info.non_nullable_vars

            # create the subset of the original key lookups, where all the nullable keys
            # are treated as null and are removed. this set will be the common key lookups,
            # used at the top-level, outside the Match. These lookups should also be removed
            # from each Match case.
            top_level_key_lookups = list(info.key_lookups)
            nullable_keys_copy = OrderedSet.from_iterable(info.nullable_keys)
            self._remove_from_key_lookups(top_level_key_lookups, nullable_keys_copy, info.non_nullable_keys)

            inner_key_lookups:list[ir.Task] = []
            for task in info.key_lookups:
                if task not in top_level_key_lookups:
                    inner_key_lookups.append(task)

            # create a compound key that will be used in place of the original keys.
            compound_key = f.var("compound_key", types.Hash)
            # the hoisted vars for Match include all the nullable keys as well as the compound key.
            hoisted:list[ir.VarOrDefault] = [ir.Default(v, None) for v in info.nullable_keys] + [compound_key]

            match_cases = self._nullable_key_combinations(info, inner_key_lookups, hoisted)

            top_level_key_lookups.append(f.match(match_cases, hoisted))
            key_logical = f.logical(tuple(top_level_key_lookups), list(info.non_nullable_keys) + hoisted)

            final_body:list[ir.Task] = [key_logical]
            for task in new_body:
                if task in info.key_lookups:
                    continue

                if isinstance(task, ir.Logical):
                    task = self._clean_logical(task, info)
                    # after the cleanup, the logical came up empty
                    if not task:
                        continue

                if isinstance(task, ir.Output):
                    annos = list(task.annotations)
                    if task.keys:
                        annos.append(f.annotation(builtins.output_keys, tuple(task.keys)))
                    final_body.append(f.output(list(task.aliases), [compound_key], annos=annos))
                else:
                    final_body.append(task)
            return f.logical(final_body, node.hoisted)
        else:
            return node if new_body is node.body else f.logical(new_body, node.hoisted)

    # generate all the combinations of nullable keys being present or not.
    # for each such combination, generate a list of lookups that will be used in the Match.
    # in total, return a list of lists of lookups, covering all the Match cases.
    def _nullable_key_combinations(
            self,
            info:ExtractInfo,
            inner_key_lookups:list[ir.Task],
            hoisted:list[ir.VarOrDefault]):
        return self._nullable_key_combinations_rec(info, [], 0, inner_key_lookups, hoisted)

    def _nullable_key_combinations_rec(
            self,
            info: ExtractInfo,
            nullable_non_null_keys: list[ir.Var],
            idx: int,
            inner_key_lookups: list[ir.Task],
            hoisted:list[ir.VarOrDefault]):

        if idx < len(info.nullable_keys):
            key = info.nullable_keys[idx]
            case1_list = self._nullable_key_combinations_rec(info, nullable_non_null_keys + [key], idx + 1, inner_key_lookups, hoisted)
            case2_list = self._nullable_key_combinations_rec(info, nullable_non_null_keys, idx + 1, inner_key_lookups, hoisted)
            case1_list.extend(case2_list)
            return case1_list
        else:
            # create a copy to mutate
            inner_key_lookups = list(inner_key_lookups)

            curr_non_null_keys = OrderedSet[ir.Var]()
            curr_null_keys = OrderedSet[ir.Var]()
            for key in info.original_keys:
                if key in info.non_nullable_keys or key in nullable_non_null_keys:
                    curr_non_null_keys.add(key)
                else:
                    curr_null_keys.add(key)

            self._remove_from_key_lookups(inner_key_lookups, curr_null_keys, curr_non_null_keys)

            # add a dummy lookup for each null key (i.e., "key = None")
            for key in info.nullable_keys:
                if key in curr_null_keys:
                    inner_key_lookups.append(f.lookup(builtins.eq, [key, None]))

            compound_key = hoisted[-1]
            assert isinstance(compound_key, ir.Var)
            # create the arguments to hash
            values: list[ir.Value] = [compound_key.type]
            for key in info.original_keys:
                assert isinstance(key.type, ir.ScalarType)
                values.append(ir.Literal(types.String, key.type.name))
                values.append(key)
            inner_key_lookups.append(ir.Construct(
                None,
                tuple(values),
                compound_key,
                OrderedSet().frozen()
            ))

            return [f.logical(inner_key_lookups, hoisted)]

    def _remove_from_key_lookups(self, lookups: list[ir.Task], vars_to_purge: OrderedSet[ir.Var], non_nullable_keys: OrderedSet[ir.Var]):
        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in lookups:
                assert isinstance(task, ir.Lookup)
                vars = helpers.vars(task.args)
                if vars[-1] in vars_to_purge:
                    lookups.remove(task)
                    new_vars = [v for v in vars if v not in vars_to_purge and v not in non_nullable_keys]
                    vars_to_purge.update(new_vars)
                    there_is_progress = True

    # remove key lookups from logicals, since they are handled in their own dedicated logical
    def _clean_logical(self, node: ir.Logical, info: ExtractInfo):
        new_body = []
        for task in node.body:
            if not(isinstance(task, ir.Lookup) and task in info.key_lookups):
                new_body.append(task)

        if new_body is node.body:
            return node

        if not new_body:
            return None

        new_hoisted = []
        for h in node.hoisted:
            if isinstance(h, ir.Default) and h.value is None and h.var in info.nullable_keys:
                continue
            new_hoisted.append(h)
        return f.logical(new_body, new_hoisted)
