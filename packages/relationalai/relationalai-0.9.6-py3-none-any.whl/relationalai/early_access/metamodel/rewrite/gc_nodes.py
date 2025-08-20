"""
Garbage collection pass that removes unused types and relations from the model.
"""
from dataclasses import dataclass, field

from relationalai.early_access.metamodel import ir, visitor, compiler
from relationalai.early_access.metamodel.util import FrozenOrderedSet

@dataclass
class GarbageCollectNodes(compiler.Pass):
    """
    A pass that removes unused types and relations from the model.
    """

    # TODO: Since sometimes models don't initially have the correct set of relations,
    # we sometimes actually end up /adding/ relations to the model here.

    # Flags to determine which nodes to gargbage collect
    # By default, we only garbage collect types and relations
    types: bool = field(default=True)
    relations: bool = field(default=True)

    @staticmethod
    def used_relations(model, engines) -> FrozenOrderedSet[ir.Relation]:
        return visitor.collect_by_type(ir.Relation, *engines, model.root, *model.annotations).frozen()

    @staticmethod
    def used_types(model, engines, relations) -> FrozenOrderedSet[ir.Type]:
        return visitor.collect_by_type(ir.Type, *engines, *relations, model.root, *model.annotations).frozen()

    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        gc_types = self.types
        gc_relations = self.relations

        # No flags set, nothing to GC
        if not gc_relations and not gc_types:
            return model

        engines = model.engines
        relations = model.relations
        types = model.types

        # Note that engines and relations are mutually dependent. If we were to also GC engines,
        # then we would need to iterate until we reach a fixed point.
        if gc_relations:
            relations = self.used_relations(model, engines)

        # Types are independent of engines and relations, so we can just collect them last
        if gc_types:
            types = self.used_types(model, engines, relations)

        return ir.Model(
            engines,
            relations,
            types,
            model.root,
            model.annotations,
        )
