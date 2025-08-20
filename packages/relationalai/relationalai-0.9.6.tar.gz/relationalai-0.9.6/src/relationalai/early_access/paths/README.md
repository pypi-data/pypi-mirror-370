# RelationalAI `paths` library

The RelationalAI `paths` library provides functionality for finding paths in a labeled
property graph that **match** a certain **pattern**, specified by a so-called
**regular path query** (RPQ).

## Basic usage: Example

The following is a minimal working example:

```py
from relationalai.early_access.builder import Model, Integer, select, String, where, define
from relationalai.early_access.builder.std import strings

from relationalai.early_access.paths.graph import Graph
from relationalai.early_access.paths.api import node, edge, path, star, match

model = Model("my_paths")

# create a labeled graph from an edge list:
edge_list = [(1, 2, "A"), (2, 3, "A"), (3, 4, "A"), (4, 5, "B"), (1, 5, "A")]
graph = Graph.from_edge_list(model, edge_list)

# specify a path pattern to match in terms of string labels:
pattern = path("A", star("A"), "B")

# specify source and target sets (optional):
sources = [1]
targets = [5]

Node = graph.Node

Source = model.Relationship("{Node} is a source node")
Target = model.Relationship("{Node} is a target node")

for src in sources:
    define(Source(Node.new(id=src)))

for tgt in targets:
    define(Target(Node.new(id=tgt)))

# specify setup for the path-finding algorithm:
paths = match(graph, pattern, Source, Target)

# convert path representation to use node IDs instead of opaque hashes:
i, k = Integer.ref(), Integer.ref()
node = graph.Node.ref()
label = String.ref()

result = select(i, k, label, node.id).where(
    paths(i, k, label, node)
)

# run the computation and display the result:
result.inspect()
```

## API

### Specifying a path pattern

A path is specified by a regular expression on edge labels, built using the following components:
- `path`: A concatenation of its arguments (separated by commas)
- `star`: Zero or more repetitions of its argument
- `plus`: One or more repetitions of its argument
- `union`: Allows any of its arguments (a single time)

### Matching a pattern
The API for matching a pattern is as follows:
```
match(graph, pattern, [Source], [Target], **kw)
```
The `Source` and `Target` sets should be `Concept`s or unary `Relationship`s containing
sets of source / target nodes, respectively. If they are not specified then all nodes are used.

The allowed keyword arguments are as follows:
- `type`
    - The type (semantics) of paths
    - Possible values:
        - `shortest`: Shortest paths
        - `walks`: Walks (all paths)
    - Default value is `shortest`

- `num_paths`
    - Specifies the maximum number of paths to return.
    - Default value is `None`, corresponding to all paths.

- `max_length`
    - Maximum length of path to return
    - Default value is 1000

## Implementation sketch

- The user's input `pattern` is converted into a finite automaton.
- We create the **product graph**, consisting of nodes of the form `(state, orig_node)`,
where `state` is a state of the automaton and `orig_node` is a node in the original graph.
- We find paths in the product graph between nodes having the automaton's initial and 
final state.
- These paths are projected back down to the user's graph.

## Notes
- Currently we use our own `Graph` `class`. This will soon be replaced by the one from the
 `graphs` library.

 ## Not yet implemented
- Reverse edges
- Group-by operations over source and target sets (e.g. "find shortest paths from *each* node in this source set to this target node)