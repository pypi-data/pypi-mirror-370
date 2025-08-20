"""
Rewrite list types to tuple or scalar types depending on how they are used.
"""
from dataclasses import dataclass, field
from typing import List, cast

from relationalai.early_access.metamodel import ir, visitor, compiler, builtins as bt
from relationalai.early_access.metamodel.util import ordered_set

@dataclass
class RewriteListTypes(compiler.Pass):
    """
    Rewrite list types to tuple or scalar types depending on how they are used.
    """
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        v = RewriteListTypesVisitor()
        result = v.walk(model)
        return result

@dataclass
class RewriteListTypesVisitor(visitor.Rewriter):
    """
    A pass that fixes the types of nodes that use ListTypes.
    """
    new_relations: List[ir.Relation] = field(default_factory=list, init=False)
    new_types: List[ir.Type] = field(default_factory=list, init=False)

    def handle_model(self, model: ir.Model, parent: None):
        result = super().handle_model(model, parent)
        relations_without_list_type = ordered_set(*[
            r for r in result.relations if not any(isinstance(f.type, ir.ListType) for f in r.fields)
        ]).frozen()
        return model.reconstruct(
            result.engines,
            relations_without_list_type | self.new_relations,
            result.types | self.new_types,
            result.root,
            result.annotations,
        )

    def handle_lookup(self, node: ir.Lookup, parent: ir.Node):
        if any(isinstance(f.type, ir.ListType) for f in node.relation.fields):
            return self._rewrite_non_aggr_relation(node, node.relation)
        else:
            return node

    def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node):
        new_aggr = self._rewrite_aggr_relation(node, node.aggregation)
        return ir.Aggregate(
            node.engine,
            new_aggr,
            node.projection,
            node.group,
            node.args,
        )

    def _rewrite_aggr_relation(self, node: ir.Aggregate, relation: ir.Relation) -> ir.Relation:
        assert len(relation.fields) >= 1
        changed = False

        if changed:
            overloads = ordered_set(*[
                self._rewrite_aggr_relation(node, overload)
                for overload in relation.overloads
            ]).frozen()

            new_relation = ir.Relation(
                relation.name,
                tuple(relation.fields),
                relation.requires,
                relation.annotations,
                overloads,
            )
            self.new_relations.append(new_relation)
            return new_relation

        return relation

    def _rewrite_non_aggr_relation(self, node: ir.Lookup, relation: ir.Relation):
        # Handle the simple varargs case: one list field and all the rest are scalar.
        # Currently this pattern is only used for `rel_primitive_hash_tuple`.
        # and `rel_primitive_solverlib_fo_appl`.
        list_field_indexes = [i for i in range(len(node.relation.fields)) if isinstance(node.relation.fields[i].type, ir.ListType)]
        if len(list_field_indexes) != 1:
            return node

        # There exactly one list field, rewrite it to a tuple type.
        i = list_field_indexes[0]
        assert isinstance(node.relation.fields[i].type, ir.ListType)
        scalar_field_count = len(node.relation.fields) - 1
        tuple_len = len(node.args) - scalar_field_count
        assert tuple_len >= 0, f"List field {i} has {tuple_len} elements, but there are only {scalar_field_count} scalar fields."

        # Flatten the list field into separate scalar fields.
        field = node.relation.fields[i]
        ft = cast(ir.ListType, field.type)
        new_fields = (
            list(node.relation.fields[0:i]) +
            [ir.Field(f"{field.name}@{j}", ft.element_type, field.input) for j in range(tuple_len)] +
            list(node.relation.fields[i+1:])
        )

        # Create new relation, adding external annotation to prevent renaming.
        # NOTE(coey): maybe this is a misuse of this annotation and there could be a nicer way to do it with overloads.
        annos = ordered_set(*node.relation.annotations, bt.external_annotation).frozen()
        new_relation = ir.Relation(node.relation.name, tuple(new_fields), node.relation.requires, annos)
        self.new_relations.append(new_relation)

        return ir.Lookup(node.engine, new_relation, node.args)
