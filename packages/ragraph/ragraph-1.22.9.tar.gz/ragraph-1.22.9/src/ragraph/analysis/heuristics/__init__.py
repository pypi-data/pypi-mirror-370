"""
# Heuristics

Heuristics are combinations of algorithms available in the other sub-packages or have an output that
does not strictly fit one of the other categories. Not all heuristics have a common argument
structure because of their more diverse nature.

## Available heuristics

- [`johnson`][ragraph.analysis.heuristics.johnson] circuit finding algorithm.
- [`markov_gamma`][ragraph.analysis.heuristics.markov_gamma] hierarchical clustering with bus
  detection heuristic.
"""

from ragraph.analysis.heuristics._johnson import johnson
from ragraph.analysis.heuristics._markov_gamma import markov_gamma

__all__ = ["johnson", "markov_gamma"]
