"""
# Comparison analysis

Comparison provides classes for comparing [`Graph` objects][ragraph.graph.Graph] to find the
commonalities (sigma) and differences (delta).

## Comparison methods

- [`sigma_graph`][ragraph.analysis.comparison.sigma_graph] to calculate the commonalities (i.e. sum)
  of a set of graphs with comparable node names.
- [`delta_graph`][ragraph.analysis.comparison.delta_graph] to calculate the differences and overlap
  between two graphs with comparable node names.
"""

from ragraph.analysis.comparison._delta import delta_graph
from ragraph.analysis.comparison._sigma import (
    SigmaMode,
    add_edges,
    add_graph,
    add_meta,
    add_nodes,
    increment_meta,
    initialize_meta,
    sigma_graph,
)
from ragraph.analysis.comparison.utils import (
    EdgeDescriptor,
    EdgeDescriptorLike,
    NodeDescriptor,
    NodeDescriptorLike,
    TagMode,
    tag,
)

__all__ = [
    "delta_graph",
    "SigmaMode",
    "add_edges",
    "add_graph",
    "add_meta",
    "add_nodes",
    "increment_meta",
    "initialize_meta",
    "sigma_graph",
    "EdgeDescriptor",
    "EdgeDescriptorLike",
    "NodeDescriptor",
    "NodeDescriptorLike",
    "TagMode",
    "tag",
]
