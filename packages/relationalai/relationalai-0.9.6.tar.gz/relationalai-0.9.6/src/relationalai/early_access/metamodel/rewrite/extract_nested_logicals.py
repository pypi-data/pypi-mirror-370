from __future__ import annotations

from relationalai.early_access.metamodel import ir, factory as f, helpers
from relationalai.early_access.metamodel.visitor import Rewriter
from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set, NameCache
from relationalai.early_access.metamodel import dependency

class ExtractNestedLogicals(Pass):

    def __init__(self):
        super().__init__()

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        # process the root node
        extractor = LogicalExtractor(model)
        root = extractor.walk(model.root, model)

        # no extractions, just return the original model
        if not extractor.ctx.top_level:
            return model

        # create a new model with the extracted top level + the new root
        body = extractor.ctx.top_level + [root]
        return ir.Model(
                model.engines,
                OrderedSet.from_iterable(model.relations).update(extractor.ctx.relations).frozen(),
                model.types,
                ir.Logical(model.root.engine, tuple(), tuple(body))
            )

class LogicalExtractor(Rewriter):
    def __init__(self, model):
        super().__init__()
        self.ctx = helpers.RewriteContext()
        self.info = dependency.analyze(model.root)
        self.name_cache = NameCache()

    def handle_logical(self, node: ir.Logical, parent: ir.Node):
        # rewrite the children
        logical = super().handle_logical(node, parent)

        # logicals that hoist vars and all vars do not have a default value will be
        # extracted, except for logicals that require special treatment of the exposed
        # variables (which is currently done by flatten), such as when the parent is a Match
        # or a Union, of if the logical has a Rank.
        if not (
            node.hoisted and
            not isinstance(parent, (ir.Match, ir.Union)) and
            all(isinstance(v, ir.Var) for v in node.hoisted) and
            not any(isinstance(c, ir.Rank) for c in node.body)
            ):
            return logical

        # compute the vars to be exposed by the extracted logical; those are keys (what
        # makes the values unique) + the values (the hoisted variables)
        exposed_vars = ordered_set()
        # start with all the inputs to this logical as keys
        # TODO - in the future we can analyze better these inputs to see if we can drop
        # some and have narrower intermediate relations
        exposed_vars.update(self.info.task_inputs(logical))
        # if there are aggregations, make sure we don't expose the projected and input vars,
        # but expose groupbys
        for child in node.body:
            if isinstance(child, ir.Aggregate):
                exposed_vars.difference_update(child.projection)
                exposed_vars.difference_update(helpers.aggregate_inputs(child))
                exposed_vars.update(child.group)
        # add the values (hoisted)
        exposed_vars.update(helpers.hoisted_vars(logical.hoisted))

        body = ordered_set()
        body.update(self.info.task_dependencies(node)) # notice info is based on the original node
        body.update(logical.body)

        name = helpers.create_task_name(self.name_cache, logical, "_nested_logical")
        connection = helpers.extract(logical, body, exposed_vars.get_list(), self.ctx, name)
        return f.lookup(connection, exposed_vars.get_list())
