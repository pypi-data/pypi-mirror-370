from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from relationalai.early_access.metamodel.rewrite import flatten
from relationalai.early_access.metamodel import ir, factory as f, helpers
from relationalai.early_access.metamodel.compiler import Pass, group_tasks
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.metamodel import dependency

class ExtractCommon(Pass):
    """
    Pass to analyze Logical bodies and extract lookups in their own Logical if it makes
    sense. The heuristic is that, if there are multiple lookups, and there are also multiple
    sibling nested logicals that will eventually be extracted by Flatten, then it makes
    sense to extract these logicals into their own "rule", and then make the original body
    just lookup this common rule.

    From:
        Logical
            Logical
                lookup1
                lookup2
                Logical1 ...
                Logical2 ...
    To:
        Logical
            Logical
                lookup1
                lookup2
                derive common
            Logical
                lookup common
                Logical1 ...
                Logical2 ...
    """

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        # create the  context
        ctx = ExtractCommon.Context(model)

        # rewrite the root
        replacement = self.handle(model.root, ctx)

        # the new root contains the extracted top level logicals and the rewritten root
        if ctx.rewrite_ctx.top_level:
            new_root = ir.Logical(model.root.engine, tuple(), tuple(ctx.rewrite_ctx.top_level + [replacement]))
        else:
            new_root = replacement

        # create the new model, updating relations and root
        return ir.Model(
            model.engines,
            OrderedSet.from_iterable(model.relations).update(ctx.rewrite_ctx.relations).frozen(),
            model.types,
            new_root
        )

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    class Context():
        def __init__(self, model: ir.Model):
            self.rewrite_ctx = helpers.RewriteContext()
            self.info = dependency.analyze(model.root)

    def handle(self, task: ir.Task, ctx: Context):
        # currently we only extract if it's a sequence of Logicals, but we could in the
        # future support other intermediate nodes
        if isinstance(task, ir.Logical):
            return self.handle_logical(task, ctx)
        else:
            return task

    def handle_logical(self, task: ir.Logical, ctx: Context):
        # create frame to process the children
        # with ctx_frame(ctx, task) as frame:
            # process the original body
            groups = group_tasks(task.body, {
                "binders": helpers.BINDERS,
                "composites": helpers.COMPOSITES
            })
            binders = groups["binders"]
            composites = groups["composites"]

            # the new body of the rewritten task
            body:OrderedSet[ir.Task] = ordered_set()

            # quick check to see if it's worth doing more analysis; we only want to extract
            # common binders if there are multiple, and there are also multiple composites
            # that will be extracted by the flatten pass later (so that they can share the
            # extracted logic).
            plan = None
            if len(binders) > 1 and composites:
                extractables = flatten.extractables(composites)
                # only makes sense to extract common if at least one nested composite will be extracted
                if extractables:
                    # make a plan to extract common tasks from the logical
                    plan = self._create_extraction_plan(binders, composites, extractables, ctx)
                    if plan and len(composites) > 1:
                        # plan is worthwhile and there are multiple composites, extract the common body and add the connection to the body
                        exposed_vars = plan.exposed_vars.get_list()
                        plan.common_reference = f.lookup(helpers.extract(task, plan.common_body, exposed_vars, ctx.rewrite_ctx, "common"), exposed_vars)
                        # if we are not distributing the reference, add to the main body
                        if not plan.distribute_common_reference:
                            body.add(plan.common_reference)

            # if we have a plan and will distribute the common reference, keep track of
            # variables still needed by the remaining tasks, as they need to be hoisted by
            # the remaining composites that get the common reference
            remaining_vars = None
            if plan and plan.distribute_common_reference:
                # add variables hoisted by this logical that are in the exposed vars, to
                # make sure they are hoisted all the way through
                remaining_vars = OrderedSet.from_iterable(helpers.hoisted_vars(task.hoisted)) & plan.exposed_vars
                for child in task.body:
                    if child in groups["other"] or child not in plan.remaining_body or child in composites:
                        continue
                    remaining_vars.update(ctx.info.task_inputs(child))
                    remaining_vars.update(ctx.info.task_outputs(child))
                remaining_vars = remaining_vars & plan.exposed_vars

            # if the plan was not used in one of the cases above, ignore it completely, we
            # are not extracting common nor distributing it around
            if plan and not plan.distribute_common_reference and not len(composites) > 1:
                plan = None

            # recursively handle children
            for child in task.body:
                # skip children that were extracted
                if plan and child not in groups["other"] and child not in plan.remaining_body and child not in composites:
                    continue

                # no plan or child is not a composite, so just add the handled to the body
                if not plan or child not in composites:
                    body.add(self.handle(child, ctx))
                    continue

                # there is a plan and the child is in composites, so...
                replacement = self.handle(child, ctx)

                # this child needs either extra local dependencies or the common reference
                if child in plan.local_dependencies or plan.distribute_common_reference:
                    # the new body will have maybe the common reference and the local deps
                    replacement_body = ordered_set()
                    hoisted = OrderedSet.from_iterable(replacement.hoisted if isinstance(replacement, helpers.COMPOSITES) else [])
                    if plan.distribute_common_reference:
                        if len(composites) == 1:
                            # if there's a single composite, just insert the whole common body into it
                            replacement_body.update(plan.common_body)
                        else:
                            # otherwise insert a clone of the reference on the extracted rule
                            assert(plan.common_reference)
                            replacement_body.add(plan.common_reference.clone())
                        # add remaining vars to hoisted, making sure there's no duplicates (due to VarOrDefault)
                        hoisted_vars = helpers.hoisted_vars(hoisted)
                        if remaining_vars:
                            hoisted = OrderedSet.from_iterable(filter(lambda v: v not in hoisted_vars, remaining_vars)) | hoisted

                    if child in plan.local_dependencies:
                        for local_dep in plan.local_dependencies[child]:
                            replacement_body.add(local_dep.clone())
                        #replacement_body.update(plan.local_dependencies[child])

                    if isinstance(replacement, ir.Logical):
                        # if the replacements is a logical, we can just add to the body
                        body.add(replacement.reconstruct(
                            replacement.engine,
                            tuple(hoisted.get_list()),
                            tuple(replacement_body.update(replacement.body).get_list()),
                            replacement.annotations
                        ))
                    else:
                        # anything else is now wrapped in a logical so that we can add the
                        # local dependencies
                        body.add(f.logical(replacement_body.add(replacement).get_list(), hoisted.get_list(), replacement.engine))
                else:
                    # child does not need extras in the body, just add it to the main body
                    body.add(replacement)

            return ir.Logical(task.engine, task.hoisted, tuple(body))

    @dataclass
    class ExtractionPlan():
        # tasks to extract to the body of the common logical
        common_body: OrderedSet[ir.Task]
        # tasks to remain in the original body
        remaining_body: OrderedSet[ir.Task]
        # variables to be exposed by the common logical
        exposed_vars: OrderedSet[ir.Var]
        # map from nested composite to the tasks in the common body that still need to be
        # included in its body, because it contains variables not exposed by the common logical
        local_dependencies: dict[ir.Task, OrderedSet[ir.Task]]
        # whether the common reference should be distributed to composites
        distribute_common_reference: bool
        # a reference to the common connection created for this plan, if any
        common_reference: Optional[ir.Lookup] = None


    def _create_extraction_plan(self, binders: OrderedSet[ir.Task], composites: OrderedSet[ir.Task], extractables: list[ir.Task], ctx: Context):
        """
        Compute a plan to extract tasks in this frame that are common dependencies
        across these composite tasks.
        """
        # compute intersection of task dependencies and inputs
        sample = composites.some()
        deps = ctx.info.task_dependencies(sample)
        if deps is None:
            return None
        # only get sibling dependencies
        common_body = binders & deps
        exposed_vars = OrderedSet.from_iterable(ctx.info.task_inputs(sample))

        # now extract from the original sets
        for composite in composites:
            if composite is sample:
                continue

            # compute sibling dependencies
            deps = ctx.info.task_dependencies(composite)
            if deps:
                for task in common_body:
                    if task not in deps:
                        common_body.remove(task)
            # compute common input vars
            t_inputs = ctx.info.task_inputs(composite)
            for v in exposed_vars:
                if v not in t_inputs:
                    exposed_vars.remove(v)

        # no vars in common, not worth to extract
        if not exposed_vars:
            return None

        for task in common_body:
            local_deps = ctx.info.local_dependencies(task)
            if local_deps:
                common_body.update(local_deps & binders)

        # not useful to extract common tasks if there's a single one
        if len(common_body) < 2:
            return None

        # check if some variable used in the common body is needed by some binder that is
        # not going to be extracted. In that case, we need to expose this variable from the
        # common body
        common_vars = ordered_set()
        for task in common_body:
            common_vars.update(ctx.info.task_outputs(task))
        common_vars = common_vars - exposed_vars
        for v in common_vars:
            for binder in binders:
                if binder not in common_body and ctx.info.task_inputs(binder) and v in ctx.info.task_inputs(binder):
                    exposed_vars.add(v)
                    break

        # check which of the original binders remain, and make sure their dependencies also stay
        remaining = ordered_set()
        for binder in binders:
            if binder not in common_body:
                remaining.add(binder)
                deps = self._compute_local_dependencies(ctx, binders, binder, common_body, exposed_vars)
                if deps:
                    remaining.update(deps)

        # for each composite, check if there are additional tasks needed, because the task
        # depends on it but it is not exposed by the vars
        local_dependencies: dict[ir.Task, OrderedSet[ir.Task]] = dict()
        for composite in composites:
            local = self._compute_local_dependencies(ctx, binders, composite, common_body, exposed_vars)
            if local:
                local_dependencies[composite] = local

        # distribute the common reference only if all of the composites are extractable and there's nothing else remaining
        distribute_common_reference = len(extractables) == len(composites) and not remaining
        return ExtractCommon.ExtractionPlan(common_body, remaining, exposed_vars, local_dependencies, distribute_common_reference)


    def _compute_local_dependencies(self, ctx: Context, binders: OrderedSet[ir.Task], composite: ir.Task, common_body: OrderedSet[ir.Task], exposed_vars: OrderedSet[ir.Var]):
        """
        The tasks in common_body will be extracted into a logical that will expose the exposed_vars.
        Compute which additional dependencies are needed specifically for this composite, because
        it depends on some tasks that are extracted to common_body but not exposed by exposed_vars.
        """

        # working list of vars we still need to fulfill
        inputs = ctx.info.task_inputs(composite)
        if not inputs:
            return None

        # vars exposed by exposed vars + tasks added to the local body
        vars_exposed = OrderedSet.from_iterable(exposed_vars)
        vars_needed = (inputs - vars_exposed)
        if not vars_needed:
            return None

        # needs = ctx.info.local_dependencies(composite) & binders | common_body
        # if needs:
        #     return needs
        # return None

        # this is a greedy algorithm that uses the first task in the common body that provides
        # a variable needed; it may result in sub-optimal extraction, but should be correct
        local_body = ordered_set()
        while(vars_needed):
            v = vars_needed.pop()
            for x in common_body:
                if x not in local_body:
                    # an x that is not yet in local_body can fulfill v
                    x_outputs = ctx.info.task_outputs(x)
                    if x_outputs and v in x_outputs:
                        # add it to local_body and add its outputs to vars exposed
                        local_body.add(x)
                        vars_exposed.add(x_outputs)
                        # but add its inputs the vars now needed
                        inputs = ctx.info.task_inputs(x)
                        if inputs:
                            vars_needed.update(inputs - vars_exposed)
        return local_body





    def _create_extraction_plan_old(self, binders: OrderedSet[ir.Task], composites: OrderedSet[ir.Task], extractables: list[ir.Task], ctx: Context):
        """
        Compute a plan to extract tasks in this frame that are common dependencies
        across these composite tasks.
        """
        # compute intersection of task dependencies and inputs
        sample = composites.some()
        deps = ctx.info.task_dependencies(sample)
        if deps is None:
            return None
        # only get sibling dependencies
        common_body = binders & deps
        exposed_vars = OrderedSet.from_iterable(ctx.info.task_inputs(sample))

        # now extract from the original sets
        for composite in composites:
            if composite is sample:
                continue

            # compute sibling dependencies
            deps = ctx.info.task_dependencies(composite)
            if deps:
                for task in common_body:
                    if task not in deps:
                        common_body.remove(task)
            # compute common input vars
            t_inputs = ctx.info.task_inputs(composite)
            for v in exposed_vars:
                if v not in t_inputs:
                    exposed_vars.remove(v)

        # no vars in common, not worth to extract
        if not exposed_vars:
            return None

        # pull the transitive closure of the intersected tasks in the common body
        chasing = True
        while(chasing):
            chasing = False
            for task in common_body:
                deps = ctx.info.task_dependencies(task)
                if deps:
                    for hop in binders & deps:
                        if hop not in common_body:
                            common_body.add(hop)
                            chasing = True

        # not useful to extract common tasks if there's a single one
        if len(common_body) < 2:
            return None

        # check if some variable used in the common body is needed by some binder that is
        # not going to be extracted. In that case, we need to expose this variable from the
        # common body
        common_vars = ordered_set()
        for task in common_body:
            common_vars.update(ctx.info.task_outputs(task))
        common_vars = common_vars - exposed_vars
        for v in common_vars:
            for binder in binders:
                if binder not in common_body and ctx.info.task_inputs(binder) and v in ctx.info.task_inputs(binder):
                    exposed_vars.add(v)
                    break

        # check with of the original binders remain, and make sure their dependencies also stay
        remaining = ordered_set()
        for binder in binders:
            if binder not in common_body:
                remaining.add(binder)
                deps = self._compute_local_dependencies_old(ctx, binder, common_body, exposed_vars)
                if deps:
                    remaining.update(deps)

        # for each composite, check if there are additional tasks needed, because the task
        # depends on it but it is not exposed by the vars
        local_dependencies: dict[ir.Task, OrderedSet[ir.Task]] = dict()
        for composite in composites:
            local = self._compute_local_dependencies_old(ctx, composite, common_body, exposed_vars)
            if local:
                local_dependencies[composite] = local

        # distribute the common reference only if all of the composites are extractable and there's nothing else remaining
        distribute_common_reference = len(extractables) == len(composites) and not remaining
        # TODO: we are forcing this for now, but we should remove the whole analysis
        distribute_common_reference = False
        return ExtractCommon.ExtractionPlan(common_body, remaining, exposed_vars, local_dependencies, distribute_common_reference)


    def _compute_local_dependencies_old(self, ctx: Context, composite: ir.Task, common_body: OrderedSet[ir.Task], exposed_vars: OrderedSet[ir.Var]):
        """
        The tasks in common_body will be extracted into a logical that will expose the exposed_vars.
        Compute which additional dependencies are needed specifically to this composite, because
        it depends on some tasks that are extracted to common_body but not exposed by exposed_vars.
        """

        # vars exposed by exposed vars + tasks added to the local body
        vars_exposed = OrderedSet.from_iterable(exposed_vars)
        # working list of vars we still need to fulfill
        inputs = ctx.info.task_inputs(composite)
        if not inputs:
            return None
        vars_needed = (inputs - vars_exposed)
        if not vars_needed:
            return None

        # this is a greedy algorithm that uses the first task in the common body that provides
        # a variable needed; it may result in sub-optimal extraction, but should be correct
        local_body = ordered_set()
        while(vars_needed):
            v = vars_needed.pop()
            for x in common_body:
                if x not in local_body:
                    # an x that is not yet in local_body can fulfill v
                    x_outputs = ctx.info.task_outputs(x)
                    if x_outputs and v in x_outputs:
                        # add it to local_body and add its outputs to vars exposed
                        local_body.add(x)
                        vars_exposed.add(x_outputs)
                        # but add its inputs the vars now needed
                        inputs = ctx.info.task_inputs(x)
                        if inputs:
                            vars_needed.update(inputs - vars_exposed)
        return local_body
