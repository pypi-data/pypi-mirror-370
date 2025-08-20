"""
# Sequencing algorithms

Sequencing algorithms search for sequences of nodes according to some objective or
logic. Simple are sorting by name and more elaborate examples sort according to Markov
transition probabilities or sequences without feedback (edges to earlier nodes).


## Available algorithms

- [`markov`][ragraph.analysis.sequence.markov] sequencing based on Markov transition probabilities
  between nodes.
- [`scc_tearing`][ragraph.analysis.sequence.scc_tearing] efficient algorithm to sort the "trivial"
  part of sequencing quickly by putting the Strongly Connected Components (largest possible cycles)
  in a non-feedback order and then "tears" iteratively according to a tearing indicator.
- [`name`][ragraph.analysis.sequence.name] just sorts nodes by their name.
- [`tarjans_dfs`][ragraph.analysis.sequence.tarjans_dfs] Tarjan's Depth First Search algorithm.
  Efficient sorting algorithm for Directed Acyclic Graphs (DAG).
- [`axis`][ragraph.analysis.sequence.axis] Typical Multi-Domain Matrix axis sorting method.


## Metrics

There are several metrics from literature available to grade sequences as well. The
metrics are documented over at [`metrics`][ragraph.analysis.sequence.metrics].


# Utilities

Finally, there are some utilities like branch-sorting (recursively sorting all branches
in a hierarchical tree instead of all leaf nodes as a whole) available in
[`utils`][ragraph.analysis.sequence.utils]:

- [`branchsort`][ragraph.analysis.sequence.branchsort] Recursively sort children within a branch or
  hierarchy using any of the above.
"""

from ragraph.analysis.sequence import metrics, utils
from ragraph.analysis.sequence._axis import axis
from ragraph.analysis.sequence._genetic import genetic
from ragraph.analysis.sequence._markov import markov
from ragraph.analysis.sequence._name import name
from ragraph.analysis.sequence._scc_tearing import scc_tearing
from ragraph.analysis.sequence._tarjan import tarjans_dfs
from ragraph.analysis.sequence.utils import branchsort

__all__ = [
    "metrics",
    "utils",
    "axis",
    "genetic",
    "markov",
    "name",
    "scc_tearing",
    "tarjans_dfs",
    "branchsort",
]
