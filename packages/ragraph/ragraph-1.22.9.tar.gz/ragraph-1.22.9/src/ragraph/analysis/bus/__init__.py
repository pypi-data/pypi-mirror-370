"""# Bus detection algorithms

Bus detection algorithms find bus nodes in graphs, also called "hubs" or "integrative
components". Typical bus nodes have a high node degree or "centrality" score.

All bus detection algorithms have the following arguments:

- `graph`: Graph to find bus nodes in.
- `root`: Root node to perform bus detection in.
- `leafs`: Optional list of leaf nodes to consider during the bus detection cycle. If
  not supplied, the leaf node descendants of the root will be considered.

They always return two lists of nodes:

- Leaf nodes that have been marked as bus nodes.
- The remaining leaf nodes.

They currently do **NOT** change anything in the graph in-place. That is up to the user.

## Available algorithms

The following algorithms are directly available after importing
[`ragraph.analysis.bus`][ragraph.analysis.bus]:

- [`gamma`][ragraph.analysis.bus.gamma]: Gamma bus detection.
"""

from ragraph.analysis.bus._gamma import gamma_bus_detection as gamma

__all__ = ["gamma"]
