import os
from typing import List, Set, Tuple, Union
import zipfile
from enum import Enum

from relationalai import dsl
from relationalai.dsl import Graph, Instance, Type, Property, create_vars, get_graph, next_id
from relationalai.metamodel import ActionType, Builtins
from relationalai.std import rel

class VarLength:
    def __init__(self, type: Type):
        self.type = type
        self.min = 1
        self.max = 1

    def __getitem__(self, key):
        if isinstance(key, slice):
            self.min = key.start
            self.max = key.stop
        else:
            raise ValueError("VarLength only supports slicing")
        return self

class PathSelection(Enum):
    ALL = "all" # return all paths between source and target
    SINGLE = "single" # return a single path between source and target
    LIMIT = "limit" # return a specified number paths between source and target, as given by parameter k.
    RANDOM = "random" # return a single randomly-chosen path between source and target, seeded with parameter seed.
    UNIFORM_RANDOM = "uniform_random" # return a single uniform randomly-chosen path between source and target, seeded with parameter seed.

class PathGroup(Enum):
    ANY = "any"
    FOREACH = "for_each"

class Strategy(Enum):
    FROM_SOURCE = "from_source"
    TWO_SIDED = "two_sided"

class PathQuery:

    def __init__(
        self,
        model: Graph,
        segments: List[Union[Instance,VarLength]],
        backwards_edge: str,
        group: PathGroup = PathGroup.FOREACH,
        selection: PathSelection = PathSelection.ALL,
        strategy: Strategy = Strategy.FROM_SOURCE,
    ):
        # create types and instance
        self._path_id = next_id()
        self._conn_relation_name = f"conn_{self._path_id}"
        self._model = model

        # create types
        self._Path = dsl.Type(model, f"Path{self._path_id}", omit_intrinsic_type_in_hash=True)
        self._PathNode = dsl.Type(model, f"PathNode{self._path_id}", omit_intrinsic_type_in_hash=True)
        self._PathEdge = dsl.Type(model, f"PathEdge{self._path_id}", omit_intrinsic_type_in_hash=True)

        # declare multivalued attributes
        self._Path.nodes.has_many()
        self._Path.edges.has_many()

        # mark these types and their attributes as @no_inline
        self._add_noinline(self._Path, [])
        self._add_noinline(self._PathNode, ["path", "index", "node_id"])
        self._add_noinline(self._PathEdge, ["path", "index", "label"])

        # create instance
        self._instance = self._Path()
        self._match_called = False

        # store path query attributes
        self._segments = segments
        self._backwards_edge = backwards_edge
        self._group = group
        self._selection = selection
        self._strategy = strategy

    def _add_noinline(self, typ, props):
        typ._type.parents.append(Builtins.NoInlineAnnotation)
        for prop in props:
            getattr(typ, prop)._prop.parents.append(Builtins.NoInlineAnnotation)

    def _match(self):
        # avoid emitting the Rel multiple times, which throws off Pathfinder
        if not self._match_called:
            self._match_called = True

            begin_var, end_var = self._match_inner()

            self._begin_var = begin_var
            self._end_var = end_var

        return self._conn_relation_name

    def _match_inner(self):
        begin_var = None
        cur_end = None

        for idx, segment in enumerate(self._segments):
            if isinstance(segment, VarLength):
                var_length_rel_name = self._var_length(idx, segment)
                seg_begin, seg_end = create_vars(2)
                getattr(rel, var_length_rel_name)(seg_begin, seg_end)

                if begin_var is None:
                    begin_var = seg_begin
                    cur_end = seg_end
                else:
                    getattr(seg_begin, self._backwards_edge) == cur_end
                    cur_end = seg_end
            else:
                next_var = segment
                if begin_var is None:
                    begin_var = next_var
                    cur_end = begin_var
                else:
                    getattr(next_var, self._backwards_edge) == cur_end
                    cur_end = next_var

        conn_relation = getattr(rel, self._conn_relation_name)
        conn_relation._rel.parents.append(Builtins.NoInlineAnnotation)
        conn_relation.add(begin_var, cur_end)

        return begin_var, cur_end

    def _var_length(self, segment_idx: int, segment: VarLength):
        # relations for each length
        prefix = f"conn_{self._path_id}_segment_{segment_idx}"

        lines = []

        for length in range(1, segment.max+1):
            length_rel_name = f"{prefix}_length_{length}"

            if length == 1:
                lines.extend([
                    f"def {length_rel_name}(a, a1):",
                    f"    {segment.type._type.name}(a) and",
                    "    a = a1"
                ])
                # would just project `(a, a)`, but that gives a
                # bunch of Rel warnings`

            else:
                prev_length_relation_name = f"{prefix}_length_{length-1}"
                lines.extend([
                    f"def {length_rel_name}(a, c):",
                    "    exists((b) |",
                    f"       {prev_length_relation_name}(a, b) and",
                    f"       {segment.type._type.name}(c) and",
                    f"       {self._backwards_edge}(c, b)",
                    "     )"
                ])

        # union them all together in overall segment relation
        lines.extend([
            f"def {prefix}(start, finish):",
            "    " + " or\n    ".join([
                f"{prefix}_length_{length}(start, finish)"
                for length in range(1, segment.max+1)
            ]),
        ])

        self._model.install_raw(
            '\n'.join(lines),
            name=f"path_{self._path_id}_segment_{segment_idx}",
        )

        return prefix


class PathInstance(Instance):

    def __init__(
        self,
        path_query: PathQuery,
    ):
        self._path_query = path_query

        self._already_called = False
        super().__init__(
            self._path_query._model,
            ActionType.Get, [self._path_query._instance],
            named={},
        )

    # implements producer API
    def _to_var(self):
        self._invoke_pathfinder()
        return super()._to_var()

    def _invoke_pathfinder(self):
        if self._already_called:
            return
        self._already_called = True

        # ensure that the pathfinder Rel library is installed
        _install_pathfinder(self._path_query._model)

        source_rel = f"source_{self._path_query._path_id}"
        target_rel = f"target_{self._path_query._path_id}"
        getattr(rel, source_rel).add(self._path_query._begin_var)
        getattr(rel, target_rel).add(self._path_query._end_var)

        shortest_paths_rel = f"shortest_paths_{self._path_query._path_id}"
        path_edge_rel = f"path_edge_{self._path_query._path_id}"
        path_node_rel = f"path_node_{self._path_query._path_id}"

        invocation = f"""
        @no_inline
        def {shortest_paths_rel} {{
            ::pathfinder::shortest_paths[
                :{self._path_query._group.value},
                :{self._path_query._selection.value},
                :{self._path_query._strategy.value},
                {self._path_query._conn_relation_name},
                {source_rel},
                {target_rel}
            ]
        }}

        @no_inline
        def {path_node_rel}(path, index, id):
            {shortest_paths_rel}(path, :node, index, id)

        @no_inline
        def {path_edge_rel}(path, index, label):
            {shortest_paths_rel}(path, :edge_label, index, label)
        """

        self._path_query._model.install_raw(invocation)

        # select out nodes
        with self._path_query._model.rule():
            path_id, index, node_label = create_vars(3)
            getattr(rel, path_node_rel)(path_id, index, node_label)
            path = self._path_query._Path.add(id=path_id)
            # TODO: avoid perf hit of going in both directions (path<->node)
            node = self._path_query._PathNode.add(path=path, index=index, value=node_label)
            path.nodes.add(node)

        # select out edges
        with self._path_query._model.rule():
            path_id, index, label = create_vars(3)
            getattr(rel, path_edge_rel)(path_id, index, label)
            path = self._path_query._Path.add(id=path_id)
            # TODO: avoid perf hit of going in both directions (path<->edge)
            edge = self._path_query._PathEdge.add(path=path, index=index, label=label)
            path.edges.add(edge)

# TODO: automatically infer this from the path query itself
def enable_on(edge: Property, filter_attrs: List[Tuple[Type, Set[str]]]):  # noqa: F821
    edge._prop.parents.append(Builtins.PQEdgeAnnotation)
    edge._prop.parents.append(Builtins.NoInlineAnnotation)
    for type, attrs in filter_attrs:
        type._type.parents.append(Builtins.PQFilterAnnotation)
        type._type.parents.append(Builtins.NoInlineAnnotation)
        for attr_name in attrs:
            prop = getattr(type, attr_name)
            prop._prop.parents.append(Builtins.PQFilterAnnotation)
            prop._prop.parents.append(Builtins.NoInlineAnnotation)

# main entry point
def path(
    segments: List[Union[Instance,VarLength]],
    backwards_edge: str,
    group: PathGroup = PathGroup.FOREACH,
    selection: PathSelection = PathSelection.ALL,
    strategy: Strategy = Strategy.FROM_SOURCE,
):
    """
    Find a path consisting of the provided segments, linked by
    the provided `backwards_edge` property.
    """

    model = get_graph()

    query = PathQuery(model, segments, backwards_edge, group, selection, strategy)

    # declare filter relations
    conn_relation_name = query._match()

    # invoke filter
    a, b = create_vars(2)
    getattr(rel, conn_relation_name)(a, b)

    # return a special Producer representing the path itself, which
    # lazily invokes Pathfinder
    return PathInstance(query)

def _get_pathfinder_source():
    # check if the current dir is in a zip file
    current_dir = os.path.dirname(__file__)
    pathfinder_path = os.path.join(current_dir, "pathfinder.rel")
    if os.path.exists(pathfinder_path):
        return open(pathfinder_path).read()
    # if we're in a zip file, read it within that
    zip_split = current_dir.split(".zip")
    zip_path = zip_split[0] + ".zip"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open('relationalai/experimental/paths/pathfinder.rel') as file:
            return file.read().decode("utf-8")

def _install_pathfinder(model: Graph):
    source = _get_pathfinder_source()
    model.install_raw(source, name="pathfinder", overwrite=True)
