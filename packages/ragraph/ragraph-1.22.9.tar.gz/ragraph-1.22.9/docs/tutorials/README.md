# RaGraph basics tutorial

## Create a Graph

Let's start by building a graph! A graph consists of nodes and edges, sometimes respectively called
vertices and arcs but we use the former. We can start with an empty [`Graph`][ragraph.graph.Graph]
object:

```python
from ragraph.graph import Graph

g = Graph()
```

You can slowly populate the empty [`Graph`][ragraph.graph.Graph] object or load nodes and edges in
bulk, both of which we'll see later this tutorial and how-to guides.

## Add a Node

When creating a [`Node`][ragraph.node.Node], all we need is a name. Let's create a node called
`"A"`.

```python
from ragraph.graph import Graph
from ragraph.node import Node

g = Graph()
a = Node("A")
g.add_node(a)

assert g["A"] == a, "It's in!"
```

What you see here, is that we create a [`Node` object][ragraph.node.Node] and add it to the
[`Graph`][ragraph.graph.Graph]. We can fetch the node from the graph via its
[`name`][ragraph.node.Node.name], which has to be unique within the [`Graph`][ragraph.graph.Graph].
Also, there are quite some attributes attached to the [`Node`][ragraph.node.Node] by default. These
are mostly metadata which you can safely ignore for now. The important thing is that it got our name
right!

## Add an Edge

An edge runs from a source node to a target node, which means that it is directed. Those two nodes
are the only required parameters to create one! Lets create a second node called `"B"` and an edge
running from `"A"` to `"B"`.

```python
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.edge import Edge

# Or from ragraph.graph import Node, Edge, Graph
g = Graph()
a = Node("A")
b = Node("B")
g.add_node(a)
g.add_node(b)
ab = Edge(a, b)
g.add_edge(ab)

assert g["A", "B"] == [ab], "All hooked up!"
```

So that concludes our first [`Edge`][ragraph.edge.Edge]! You can query all edges between two nodes
(you can add any amount!) by supplying both a source and target [`Node`][ragraph.node.Node] name as
a tuple. Again, the same metadata properties have been added as we've seen before, which you can
safely ignore.

!!! note

    Because we did not supply a `name` to the [`Edge`][ragraph.edge.Edge], it has been assigned a
    [UUID](https://docs.python.org/3/library/uuid.html#uuid.uuid4) (Universally Unique IDentifier)
    to recognize it by.

## Create a hierarchical Graph

Suppose we want to create a hierarchial [`Graph`][ragraph.graph.Graph] where nodes have parent-child
relationships. You can! Let's create a [`Graph`][ragraph.graph.Graph] with four children and then
create a parent-child relationship.

```python
from ragraph.graph import Graph
from ragraph.node import Node

g = Graph(nodes=[Node(i) for i in "ABCD"])  # Creates four nodes.
g["A"].children = [g[i] for i in "BCD"]  # Set children of "A".

assert g["B"] in g["A"].children, "Yup, B is part of A's children!"
assert g["B"].parent == g["A"], "B got a parent node!"
```

Which means the children have been added to `A`'s children property. The parent relationship is
updated automatically, too, though!

It's perfectly possible to add edges to hierarchical graphs. There are no restrictions as to which
source nodes can target which target nodes, as long as both exist in the graph.

!!! note

    Some algorithms leverage parent-child relationships and the edges between descendant when
    calculating weights between nodes, so make sure you understand how the weights or relations
    between nodes are calculated in an algorithm so you provide it with the correct input.

## Using the metadata fields

In RaGraph, both [`Node`][ragraph.node.Node], [`Edge`][ragraph.edge.Edge] and
[`Graph`][ragraph.graph.Graph] objects support an identical metadata structure. This structure
consists of the following elements:

- `kind`: The main category or _domain_ of a node or edge.
- `labels`: A list of labels you can to attach to any node or edge.
- `weights`: A dictionary of keys to (numeric) values. For instance a `cost` property for a node or
  the `strength` of an edge.
- `annotations`: A rather flexible `ragraph.generic.Annotations` object you can store pretty much
  any additional information in. You can initialize it using a dictionary as you will see in the
  following example.

An example of a fully annotated [`Node`][ragraph.node.Node] or [`Edge`][ragraph.edge.Edge] would
then be:

```python
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.edge import Edge

fancy_node = Node(
    name="fancy node",
    kind="exquisite",
    labels=["grand", "grotesque"],
    weights={"cost": 1e6},
    annotations={"comment": "Some additional information."},
)
fancy_edge = Edge(
    source=fancy_node,
    target=fancy_node,
    name="fancy edge",
    kind="exquisite",
    labels=["grand", "grotesque"],
    weights={"cost": 1e6},
    annotations={"comment": "Some additional information."},
)
fancy_graph = Graph(nodes=[fancy_node], edges=[fancy_edge])

assert fancy_graph["fancy node"].annotations.comment == "Some additional information."
```

Where most properties are fairly explanatory, [the `Annotations`
object][ragraph.generic.Annotations] might need a little explaining. It's essentially a class you
can supply any (keyword) arguments or a dictionary to. The keys are used to form property names.
Keep in mind that it is recommended to only add serializable objects to this class, so you can
export and import your data with ease.

## As a dictionary

All of the [`Node`][ragraph.node.Node], [`Edge`][ragraph.edge.Edge],
[`Annotations`][ragraph.generic.Annotations], and [`Graph`][ragraph.graph.Graph] classes feature a
`json_dict` property which is a regular Python dictionary containing only serializable data that's
readily exportable using Python's default `json` module or most other Python I/O packages.

Let's review the it for some of the previously introduced variables:

```python
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.edge import Edge

fancy_node = Node(
    name="fancy node",
    kind="exquisite",
    labels=["grand", "grotesque"],
    weights={"cost": 1e6},
    annotations={"comment": "Some additional information."},
)
fancy_edge = Edge(
    source=fancy_node,
    target=fancy_node,
    name="fancy edge",
    kind="exquisite",
    labels=["grand", "grotesque"],
    weights={"cost": 1e6},
    annotations={"comment": "Some additional information."},
)
fancy_graph = Graph(nodes=[fancy_node], edges=[fancy_edge])

assert fancy_node.as_dict() == {
    "name": "fancy node",
    "parent": None,
    "children": [],
    "is_bus": False,
    "kind": "exquisite",
    "labels": ["grand", "grotesque"],
    "weights": {"cost": 1000000.0},
    "annotations": {"comment": "Some additional information."},
}
assert fancy_edge.as_dict() == {
    "source": "fancy node",
    "target": "fancy node",
    "name": "fancy edge",
    "kind": "exquisite",
    "labels": ["grand", "grotesque"],
    "weights": {"cost": 1000000.0},
    "annotations": {"comment": "Some additional information."},
}
```

!!! note

    This works for [`Graph`][ragraph.graph.Graph]'s themselves, too, but you get the point.

## Node properties

Nodes have specific properties such as [`width`][ragraph.node.Node.width],
[`depth`][ragraph.node.Node.depth], and [`height`][ragraph.node.Node.height] to name a few. These
often come into play when analyzing hierarchies of nodes using
[clustering](../how-to-guides/clustering.md) or [bus detection](../how-to-guides/bus.md) algorithms.

A short summary of most of the available properties:

- [`width`][ragraph.node.Node.width]: The number of children this node has.
- [`depth`][ragraph.node.Node.depth]: The number of consecutive ancestor (parent) nodes up until the
  root node. If this is a root node, the depth is 0.
- [`height`][ragraph.node.Node.height]: The maximum number of consecutive descendant (child) nodes
  until a leaf node is reached. If this is a leaf node, the height is 0.
- [`is_leaf`][ragraph.node.Node.is_leaf]: Whether this node has no children and thus is a leaf node.
- [`is_root`][ragraph.node.Node.is_root]: Whether this node is a root node and thus has no parent.
- [`is_bus`][ragraph.node.Node.is_bus]: Whether this node is a highly integrative node within its
  network of siblings. See [bus detection](../how-to-guides/bus.md).

## Graph utilities

Up until now we've more or less treated the [`Graph`][ragraph.graph.Graph] object as a
[`Node`][ragraph.node.Node] and [`Edge`][ragraph.edge.Edge] store but it is more than that! The
[`Graph`][ragraph.graph.Graph] object has several useful methods, too, which we will explore in this
section.

### Kinds, labels, weights

To check what kinds, labels, or weights have been used, you can use any of the following properties
on any [`Graph`][ragraph.graph.Graph] object:

- [`graph.node_kinds`][ragraph.graph.Graph.node_kinds]
- [`graph.edge_kinds`][ragraph.graph.Graph.edge_kinds]
- [`graph.node_labels`][ragraph.graph.Graph.node_labels]
- [`graph.edge_labels`][ragraph.graph.Graph.edge_labels]
- [`graph.node_weight_labels`][ragraph.graph.Graph.node_weight_labels]
- [`graph.edge_weight_labels`][ragraph.graph.Graph.edge_weight_labels]

### Querying nodes

So far, we've discussed getting nodes by name using `graph["node name"]`. However, you can use any
of the following methods to retrieve specific nodes as well:

- [`graph.roots`][ragraph.graph.Graph.roots]: Get all nodes in the graph that have no parent.
- [`graph.leafs`][ragraph.graph.Graph.leafs]: Get all nodes in the graph that have no children.
- [`graph.targets_of`][ragraph.graph.Graph.targets_of]: Yield all nodes that have an incoming edge
  from your given node.
- [`graph.sources_of`][ragraph.graph.Graph.sources_of]: Yield all nodes that have an edge targeting
  your given node.

### Querying edges

Previously, we have retrieved edges using `graph["source name", "target name"]` or via their edge ID
using `graph.id_to_edge[id]`. Similarly to the nodes, we have the following methods to retrieve
specific edges:

- [`graph.edges_from`][ragraph.graph.Graph.edges_from]: Yield all edges originating from your given
  node.
- [`graph.edges_to`][ragraph.graph.Graph.edges_to]: Yield all edges that target your given node.
- [`graph.edges_between`][ragraph.graph.Graph.edges_between]: Yield all edges between two nodes.
- [`graph.edges_between_all`][ragraph.graph.Graph.edges_between_all]: Yield all edges between a set
  of sources and targets.

### Calculate an adjacency matrix

An adjacency matrix represents the sum of edge weights between sets of nodes. The nodes are
identically ordered on both the matrix' axes. A cell value on `[i, j]` then denotes the sum of edge
weights of edges going from the `j` node (column) to the `i` node (row). This follows the IR/FAD
(inputs in rows, feedback above diagonal) convention. Here is a little example of the
[`graph.get_adjacency_matrix` method][ragraph.graph.Graph.get_adjacency_matrix]:

```python
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.edge import Edge

a = Node("a")
b = Node("b")
nodes = [a, b]
edges = [
    Edge(a, a, weights={"strength": 1}),
    Edge(b, a, weights={"flow": 3}),
    Edge(a, b, weights={"strength": 9}),
]
g = Graph(nodes=nodes, edges=edges)
g.get_adjacency_matrix(loops=True)
```

Or, if you want to omit self loops and only look at the `flow` weights:

```python
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.edge import Edge

a = Node("a")
b = Node("b")
nodes = [a, b]
edges = [
    Edge(a, a, weights={"strength": 1}),
    Edge(b, a, weights={"flow": 3}),
    Edge(a, b, weights={"strength": 9}),
]
g = Graph(nodes=nodes, edges=edges)
g.get_adjacency_matrix(loops=True)

adj = g.get_adjacency_matrix(loops=False, only=["flow"])
assert adj.tolist() == [
    [0, 3],
    [0, 0],
]
```

Please take a look at the method's documentation for more information:
[`ragraph.graph.Graph.get_adjacency_matrix`][ragraph.graph.Graph.get_adjacency_matrix].

!!! note

    Similarly, you can calculate a mapping matrix using [`ragraph.graph.Graph.get_mapping_matrix`][ragraph.graph.Graph.get_mapping_matrix]
    where the rows and columns do **not** need to be symmetrical. This is commonly used to calculate
    a mapping from nodes of one domain (node kind) to another.

## Where to next?

Feel free to check either the [How-to guides](../how-to-guides/README.md) for more specific use
cases, or dive straight into the [Reference](../reference/README.md) for some nicely formatted
reference documentation and get coding!
