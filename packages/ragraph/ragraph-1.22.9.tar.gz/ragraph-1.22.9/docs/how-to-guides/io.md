# Graph I/O

This page covers importing and exporting [`Graph` objects][ragraph.graph.Graph] from and to
different (file) formats using [the `ragraph.io` module][ragraph.io]. Among the available formats
are JSON, YAML, XML, 2D matrices, and more. Feel free to head over to the module's reference
documentation to see them all!

The importing and exporting of JSON is probably the most extensive implementation, closely followed
by CSV. Some formats are only partly supported, where in most cases it features either importing to
[a `Graph` object][ragraph.graph.Graph] or merely exporting one.

## JSON

A [`Graph`][ragraph.graph.Graph] can be translated both from and to a JSON file or encoded JSON
string. These are all based on the JSON dictionary representations of the objects in the graph and
handled by [the `ragraph.io.json` module][ragraph.io.json].

Take a look at [this JSON file](../assets/simple.json) for an exemplary JSON file. It may seem
relatively verbose, but is little more than a JSON dump of [the `json_dict`
property][ragraph.graph.Graph.json_dict] property of an otherwise simple
[`Graph`][ragraph.graph.Graph].

Importing it goes like this:

```python
from ragraph.io.json import from_json

g = from_json("docs/assets/simple.json")
```

Which loads a [`Graph`][ragraph.graph.Graph] into `g` with six nodes (`"a"` through `"f"`) with a
couple of edges between them.

If you already have a JSON encoded string loaded into a variable, you can also supply this by using:
`from_json(enc=my_string_variable)`.

Exporting the graph is rather similar:

```python
from ragraph.io.json import from_json, to_json

g = from_json("docs/assets/simple.json")
enc = to_json(g, path=None)  # Converts it into a JSON string.
# to_json(g, path="./output.json")  # Writes it to a JSON file.
```

Which by setting `path=None` will give you a JSON string representation of the graph. When actually
setting the path to a filepath, the string will not be returned and written to that filepath
instead.

## CSV

The CSV format is probably one of the most compact formats we support. To import from CSV you need
both a **nodes** and an **edges** CSV file. The functionality is included in [the `ragraph.io.csv`
module][ragraph.io.csv].

The minimum requirement to a nodes file is that each node has a `name`. A basic nodes file thus
looks like [simple_nodes.csv](../assets/simple_nodes.csv). This file will generate six nodes named
`"a"` through `"f"` when imported, with all other [`Node`][ragraph.node.Node] arguments left to
their defaults.

The minimum edges file needs a `source` and a `target` column. These should refer to the source and
target node of each edge, such as the [simple_edges.csv](../assets/simple_edges.csv).

Importing these can be done using the following snippet:

```python
from ragraph.io.csv import from_csv

nodes_path = "docs/assets/simple_nodes.csv"
edges_path = "docs/assets/simple_edges.csv"
g = from_csv(nodes_path, edges_path)
assert len(g.nodes) == 6, "Should have gotten 6 nodes."
```

You can tweak some additional settings in [the `from_csv` method][ragraph.io.csv.from_csv] like the
CSV delimiter and some parameters to indicate which column includes which metadata.

## Matrix

A [`Graph`][ragraph.graph.Graph] and its adjacency matrix are closely related. To facilitate quick
transitions between these representations, we included [the `ragraph.io.matrix`
module][ragraph.io.matrix]. This allows you to transition back and forth from a list of lists or
nested numpy array and [a `Graph` object][ragraph.graph.Graph]. A small example:

```python
from ragraph.io.matrix import from_matrix, to_matrix

adj = [
    [0, 1, 0],
    [2, 0, 1],
    [9, 9, 9],
]
g = from_matrix(adj)

# And the other way around!
adj = to_matrix(g, loops=True)
assert adj.tolist() == [
    [0, 1, 0],
    [2, 0, 1],
    [9, 9, 9],
]
```

We usually default to leaving out edges that are self-loops (e.g. the diagonal is 0), but if you
would like to include them, just set `loops=True`. There are some tweaks for hierarchical graphs,
too. Please refer to the [`ragraph.io.matrix`][ragraph.io.matrix] module's documentation for that.

## Other formats

For other formats, including the Elephant Specification Language, please refer to [the `ragraph.io`
module reference documentation][ragraph.io].
