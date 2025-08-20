"""
# Similarity analyses

Graph similarity is often expressed as a metric, where nodes and edges are scanned for similar
patterns, properties, or other aspects. There are three levels of equivalence, being structural,
automorphic, or regular equivalence. Where each of the former implies all latter equivalences,
respectively.

## Available analyses

The following algorithms are directly accessible after importing
[`ragraph.analysis.similarity`][ragraph.analysis.similarity]:

* [`jaccard_index`][ragraph.analysis.similarity.jaccard_matrix]: Jaccard Similarity Index of two
  objects based on the number properties they both possess divided by the number of properties
  either of them have.
* [`jaccard_matrix`][ragraph.analysis.similarity.jaccard_matrix]: Jaccard Similarity Index between a
  set of objects stored in a square matrix.

Note:
    Both Jaccard methods require a callable that takes an object and returns a list of booleans
    representing the possession of a property (the `on` argument). Some examples are included in the
    [`ragraph.analysis.similarity.utils`][ragraph.analysis.similarity.utils] module, like
    [`ragraph.analysis.similarity.utils.on_hasattrs`][ragraph.analysis.similarity.utils.on_hasattrs].
"""

from ragraph.analysis.similarity._jaccard import jaccard_index, jaccard_matrix
from ragraph.analysis.similarity._similarity import SimilarityAnalysis

__all__ = ["jaccard_index", "jaccard_matrix", "SimilarityAnalysis"]
