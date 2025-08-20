# Bus detection

Bus detection equates to finding the highly integrative nodes in a network (graph). The terminology
_bus_ originates from the bus component often found in electronic hardware. Most other components
plug into or communicate via the bus. The bus detection algorithms are grouped into the
[`ragraph.analysis.bus` module][ragraph.analysis.bus].

Bus nodes often display high node degrees (number of incoming and outgoing edges) or other measures
of _centrality_. Currently the only algorithm that is implemented is the [`gamma` bus
detection][ragraph.analysis.bus]. It utilizes the degree distribution of nodes and distinguishes bus
nodes by a factor _gamma_ with respect to the median of node degrees within a graph (or graph
slice).

Detecting buses does **not** change any values or properties within the graph and merely returns the
detection results. This is on purpose, as you might provide any groups of nodes that aren't
necessarily _siblings_ in any way.

## Example

Let's use the [Ford Climate Control System dataset][ragraph.datasets.climate_control] that is a
graph that models the system architecture of a climate control system you would find in your car. We
can use the following snippet to return the names of the nodes that would be considered bus nodes
and those that are not:

```python
from ragraph import datasets
from ragraph.analysis import bus

g = datasets.get("climate_control")
bus, nonbus = bus.gamma(g, leafs=g.leafs, gamma=2.0, names=True)
assert bus == [
    "Command Distribution",
    "Compressor",
    "Air Controls",
]
assert nonbus == [
    "Radiator",
    "Engine Fan",
    "Heater Core",
    "Heater Hoses",
    "Condenser",
    "Evaporator Case",
    "Evaporator Core",
    "Accumulator",
    "Refrigeration Controls",
    "Sensors",
    "Actuators",
    "Blower Controller",
    "Blower Motor",
]
```

Where we can see that we detect three nodes as the bus nodes for `gamma=2.0`.

It is up to the user to interpret the results of this analysis! (or any analysis, really)

Suppose we want to incorporate these results in our [`Graph`][ragraph.graph.Graph], we could then do
the following:

```python
from ragraph import datasets
from ragraph.analysis import bus
from ragraph.node import Node

g = datasets.get("climate_control")
bus, nonbus = bus.gamma(g, leafs=g.leafs, gamma=2.0, names=True)

g.add_node(Node("system", children=g.leafs))

for name in bus:
    g[name].is_bus = True
```

We add a parent [`Node`][ragraph.node.Node] here named `"system"` to indicate the system boundary.
This is intentional and even required! The [`is_bus`][ragraph.node.Node.is_bus] property namely
indicates that a Node is a bus **within** or **for** the parent (sub-)system that we just defined.

For instance, you could have a complete hierarchy of nodes and have a **local** bus node that isn't
highly integrative for your the complete system (all nodes), but does fulfill that role in a
sub-system located deeper in your hierarchy.
