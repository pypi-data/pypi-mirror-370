"""
# Clustering algorithms

Clustering algorithms detect (nested) clusters of nodes in graphs that are relatively
tightly connected by means of their edges. Both hierarchical and flat clustering
algorithms are provided.

Apart of algorithm specific parameters, all of them feature the same basic parameters:

- `graph`: Graph to cluster containing the relevant nodes and edges.
- `leafs`: Optional list of leaf nodes to cluster. If not provided all the graph's
  leaf nodes are selected.
- `inplace`: Boolean toggle whether to create the new cluster nodes in the provided
  graph or provided a deepcopy of the graph with only the leaf nodes, their edges and
  newly created cluster nodes.

## Available algorithms

- [`markov`][ragraph.analysis.cluster.markov]
- [`hierarchical_markov`][ragraph.analysis.cluster.hierarchical_markov]
- [`tarjans_scc`][ragraph.analysis.cluster.tarjans_scc]
"""

from ragraph.analysis.cluster._markov import (
    MarkovFlow,
    MarkovRelative,
    calculate_tpm,
    create_clusters,
    get_sink_matrix,
    hierarchical_markov,
    markov,
    prune_matrix,
)
from ragraph.analysis.cluster._tarjan import tarjans_scc

__all__ = [
    "hierarchical_markov",
    "markov",
    "tarjans_scc",
    "calculate_tpm",
    "create_clusters",
    "create_parent",
    "get_sink_matrix",
    "MarkovFlow",
    "MarkovRelative",
    "prune_matrix",
]
