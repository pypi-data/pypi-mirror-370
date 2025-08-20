# Clustering analysis

This page described how to use the available algorithms in RaGraph's
[`ragraph.analysis.cluster`][ragraph.analysis.cluster] module as well as some in the
[`ragraph.analysis.heuristics`][ragraph.analysis.heuristics] module.

In general, clustering a [`Graph`][ragraph.graph.Graph] involves the grouping of components that
have many mutual or very strong dependencies (edges). One can also compute complete hierarchies by
clustering nodes in an iterative fashion (e.g. clusters of clusters).

# Single level clustering

You can tweak some parameters later, but at minimal it suffices to supply a
[`Graph`][ragraph.graph.Graph]. Let's apply the [Markov clustering algorithm
`ragraph.analysis.cluster.markov`][ragraph.analysis.cluster.markov] to the [Ford Climate Control
System dataset][ragraph.datasets.climate_control]:

```python
from ragraph import datasets
from ragraph.analysis import cluster

g = datasets.get("climate_control")
g, parents = cluster.markov(g, names=True, inplace=True)
assert parents == ['node.node0', 'node.node1', 'node.node2']
```

Which shows that our graph has been clustered into three new nodes, with some default naming for
them. Lets review the hierarchy dictionary to view this in more detail:

```python
from ragraph import datasets
from ragraph.analysis import cluster

g = datasets.get("climate_control")
g, parents = cluster.markov(g, names=True, inplace=True)
h = g.get_hierarchy_dict()

assert h == {
    "node.node0": {
        "Radiator": {},
        "Engine Fan": {},
        "Condenser": {},
        "Compressor": {},
        "Evaporator Core": {},
        "Accumulator": {},
    },
    "node.node1": {
        "Heater Core": {},
        "Heater Hoses": {},
        "Evaporator Case": {},
        "Actuators": {},
        "Blower Controller": {},
        "Blower Motor": {},
    },
    "node.node2": {
        "Refrigeration Controls": {},
        "Air Controls": {},
        "Sensors": {},
        "Command Distribution": {},
    },
}
```

The [`markov`][ragraph.analysis.cluster.markov] algorithm is a single-level clustering algorithm,
that will give you a single set of parent nodes (if any) for the given leaf nodes as input. If you
only supply a [`Graph`][ragraph.graph.Graph] it will use all the graph's leaf nodes.

# Hierarchical clustering

An example of hierarchical clustering using the [Hierarchical Markov clustering algorithm
`ragraph.analysis.cluster.hierarchical_markov`][ragraph.analysis.cluster.hierarchical_markov] would be the
following:

```python
from ragraph import datasets
from ragraph.analysis import cluster

g = datasets.get("climate_control")
g, roots = cluster.hierarchical_markov(g, inplace=True)
h = g.get_hierarchy_dict()
assert h == {
    "node.node3": {
        "node.node0": {
            "Radiator": {},
            "Engine Fan": {},
            "Condenser": {},
            "Compressor": {},
            "Evaporator Core": {},
            "Accumulator": {},
        },
        "node.node1": {
            "Heater Core": {},
            "Heater Hoses": {},
            "Evaporator Case": {},
            "Actuators": {},
            "Blower Controller": {},
            "Blower Motor": {},
        },
        "node.node2": {
            "Refrigeration Controls": {},
            "Air Controls": {},
            "Sensors": {},
            "Command Distribution": {},
        },
    }
}
assert len(roots) == 1, "We found only one root."
```

Where we can see that all three earlier found clusters have now also been recursively grouped
together into a single root because of the interactions between their leaf nodes.
