# Similarity analysis

The design of a product family requires the creation of a basic product
architecture from which all product family members can be derived. By
analyzing the similarity of products within an existing product
portfolio one can get an indication of which and how many product
variants have to be supported by the architecture.

## Input

The input for a similarity analysis is a domain mapping matrix (or bipartite graph) that maps
individual products from the portfolio to attributes that characterize the functionality and designs
of the products. The [`ragraph.datasets`][ragraph.datasets] module contains an example data set for
performing a similarity analysis. So let's get started and load the 'similarity' dataset and
visualize it using [`ragraph.plot.dmm`][ragraph.plot.dmm]:

```python
from ragraph import datasets, plot

g = datasets.get("similarity")

fig = plot.dmm(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
    sort=False,
)
fig.write_image("./docs/generated/dmm.svg")
```

<figure markdown>
![product--attribute domain mapping
matrix.](../generated/dmm.svg)
<figcaption>
product--attribute domain mapping matrix.
</figcaption>
</figure>

The figure above shows the resulting domain mapping matrix (DMM), in which twelve products (columns)
are mapped to ten attributes (rows). A mark at position $i,j$ indicates that product $j$ is
characterized by attribute $i$.

In selecting attributes for performing a similarity analysis you should balance the attribute
granularity level. That is, very fine grained (detailed) attributes will yield a very sparse mapping
matrix, while very coarse (high level) attributes will yield a very dense mapping matrix. Moreover,
you should take care in ensuring that the attributes are non-overlapping. In general, it is advised
to use attributes that define functionality, working-principles, and embodiments of product(s)
(modules).

Once you have defined your graph, mapping products to attributes, you can use the [the
`SimilarityAnalysis` object][ragraph.analysis.similarity.SimilarityAnalysis] to perform the
similarity analysis. First, you have to instantiate the object for which a minimal example is shown
below:

```python
from ragraph import datasets
from ragraph.analysis.similarity import SimilarityAnalysis

g = datasets.get("similarity")

sa = SimilarityAnalysis(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
)
```

[The `SimilarityAnalysis` object][ragraph.analysis.similarity.SimilarityAnalysis] object requires
three parameters: `rows` which is a list of [`Node` objects][ragraph.node.Node] which are the row
elements of a DMM (in this case attributes), `cols` which is a list of [`Node`
objects][ragraph.node.Node] which are the column elements of a DMM (in this case products), and
`edges` which is a list of [`Edge` objects][ragraph.edge.Edge] that map column elements to row
elements.

Internally, [the `jaccard_matrix`][ragraph.analysis.similarity.jaccard_matrix] is calculated for
both the columns elements as the row elements, which are stored within the
[`row_similarity_matrix`][ragraph.analysis.similarity.SimilarityAnalysis.row_similarity_matrix] and
[`col_similarity_matrix`][ragraph.analysis.similarity.SimilarityAnalysis.col_similarity_matrix]
attributes:

```python
from ragraph import datasets
from ragraph.analysis.similarity import SimilarityAnalysis

g = datasets.get("similarity")

sa = SimilarityAnalysis(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
)
print(sa.row_similarity_matrix)
"""
[[1.         0.         0.         0.25       0.         0.25
  0.16666667 0.2        0.         0.        ]
 [0.         1.         0.         0.         0.         0.
  0.2        0.         0.         0.33333333]
 [0.         0.         1.         0.         0.5        0.
  0.16666667 0.         0.25       0.        ]
 [0.25       0.         0.         1.         0.         0.
  0.         0.25       0.         0.        ]
 [0.         0.         0.5        0.         1.         0.
  0.16666667 0.         0.25       0.        ]
 [0.25       0.         0.         0.         0.         1.
  0.2        0.25       0.         0.        ]
 [0.16666667 0.2        0.16666667 0.         0.16666667 0.2
  1.         0.         0.         0.2       ]
 [0.2        0.         0.         0.25       0.         0.25
  0.         1.         0.         0.        ]
 [0.         0.         0.25       0.         0.25       0.
  0.         0.         1.         0.        ]
 [0.         0.33333333 0.         0.         0.         0.
  0.2        0.         0.         1.        ]]
"""

print(sa.col_similarity_matrix)
"""
[[1.         0.25       0.33333333 0.         0.33333333 0.
  0.         0.         0.         0.25       0.         0.        ]
 [0.25       1.         0.         0.25       0.25       0.25
  0.25       0.         0.         0.2        0.         0.        ]
 [0.33333333 0.         1.         0.         0.33333333 0.
  0.         0.         0.         0.         0.         0.        ]
 [0.         0.25       0.         1.         0.         0.
  0.33333333 0.         0.         0.         0.33333333 0.        ]
 [0.33333333 0.25       0.33333333 0.         1.         0.
  0.         0.         0.         0.25       0.         0.        ]
 [0.         0.25       0.         0.         0.         1.
  0.33333333 0.         0.         0.         0.33333333 0.        ]
 [0.         0.25       0.         0.33333333 0.         0.33333333
  1.         0.         0.         0.         0.33333333 0.        ]
 [0.         0.         0.         0.         0.         0.
  0.         1.         0.33333333 0.25       0.         0.33333333]
 [0.         0.         0.         0.         0.         0.
  0.         0.33333333 1.         0.66666667 0.         0.33333333]
 [0.25       0.2        0.         0.         0.25       0.
  0.         0.25       0.66666667 1.         0.         0.25      ]
 [0.         0.         0.         0.33333333 0.         0.33333333
  0.33333333 0.         0.         0.         1.         0.        ]
 [0.         0.         0.         0.         0.         0.
  0.         0.33333333 0.33333333 0.25       0.         1.        ]]
"""
```

The data from these matrices are stored within the [internal `graph`
property][ragraph.analysis.similarity.SimilarityAnalysis.graph]. This graph is a [regular `Graph`
object][ragraph.graph.Graph] which you can be visualized using the
[`ragraph.plot`][ragraph.plot] module:

```python
from ragraph import datasets, plot
from ragraph.analysis.similarity import SimilarityAnalysis

g = datasets.get("similarity")

sa = SimilarityAnalysis(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
)

fig = plot.mdm(
    leafs=sa.graph.leafs,
    edges=sa.graph.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=["similarity"],
        )
    ),
)
fig.write_image("./docs/generated/smdm1.svg")
```

<figure markdown>
![Product--attribute multi-domain-matrix showing similarity
weights.](../generated/smdm1.svg)
<figcaption>
Product--attribute multi-domain-matrix showing similarity weights.
</figcaption>
</figure>

This figure shows the resulting product--attribute multi-domain-matrix (MDM) in which similarity
weights are displayed.

## Pruning

If a similarity matrix is very dense, you may want to prune the matrix by removing all values below
a certain threshold. You can prune the matrices by setting the values of the [`col_sim_threshold`
property][ragraph.analysis.similarity.SimilarityAnalysis.col_sim_threshold] and [`row_sim_threshold`
property][ragraph.analysis.similarity.SimilarityAnalysis.row_sim_threshold] attributes:

```python
from ragraph import datasets, plot
from ragraph.analysis.similarity import SimilarityAnalysis

g = datasets.get("similarity")

sa = SimilarityAnalysis(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
)

sa.row_sim_threshold = 0.20  # Set a minimum 20% threshold.
sa.col_sim_threshold = 0.30  # Set a minimum 30% threshold.

fig = plot.mdm(
    leafs=sa.graph.leafs,
    edges=sa.graph.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=["similarity"],
        )
    ),
)
fig.write_image("./docs/generated/smdm2.svg")
```

<figure markdown>
![Pruned product--attribute multi-domain-matrix showing similarity weights.](../generated/smdm2.svg)
<figcaption>
Pruned product--attribute multi-domain-matrix showing similarity weights.
</figcaption>
</figure>

By changing the value of these attributes, the
[`SimilarityAnalysis.graph`][ragraph.analysis.similarity.SimilarityAnalysis.graph] attribute will
automatically update, as show in the figure below in which all edges with a similarity weight below
the set thresholds are removed. You can also set these in the class constructor directly.

## Clustering

The aim of a similarity analysis is to find groups (clusters) of products that are similar and could
therefore be standardized. Similarly, one could search for groups (clusters) of attributes that have
high similarity, which implies that they are often found together within products. To highlight
these clusters you can use the
[`cluster_rows`][ragraph.analysis.similarity.SimilarityAnalysis.cluster_rows] and
[`cluster_cols`][ragraph.analysis.similarity.SimilarityAnalysis.cluster_cols] methods:

```python
from ragraph import datasets, plot
from ragraph.analysis.similarity import SimilarityAnalysis

g = datasets.get("similarity")

sa = SimilarityAnalysis(
    rows=[n for n in g.nodes if n.kind == "attribute"],
    cols=[n for n in g.nodes if n.kind == "product"],
    edges=g.edges,
)

sa.row_sim_threshold = 0.20  # Set a minimum 20% threshold.
sa.col_sim_threshold = 0.30  # Set a minimum 30% threshold.

sa.cluster_rows(alpha=2.0, beta=2.0, mu=2.0)
sa.cluster_cols(alpha=2.0, beta=2.0, mu=2.0)

sa.row_sim_threshold = 0.0  # Release threshold to show all data.
sa.col_sim_threshold = 0.0  # Release threshold to show all data.
fig = plot.mdm(
    leafs=sa.graph.leafs,
    edges=sa.graph.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=["similarity"],
        )
    ),
)
fig.write_image("./docs/generated/smdm3.svg")
```

<figure markdown>
![Clustered product--attribute similarity
multi-domain-matrix.](../generated/smdm3.svg)
<figcaption>
Clustered product--attribute similarity multi-domain-matrix.
</figcaption>
</figure>

The figure above shows the outcome of the clustering algorithm, with the thresholds released
post-clustering. By default the [`ragraph.analysis.cluster.markov`][ragraph.analysis.cluster.markov] algorithm. You could, however,
provide a different algorithm by setting the `algo` argument if desired.

!!! note

    We reset the similarity thresholds to 0.0 to ensure that all data is displayed. In the MDM
    above one can find three product clusters and three attribute clusters. The first product
    cluster maps to the first attribute cluster, the second product cluster primarily maps to the
    third attribute cluster, and the third product cluster primarily maps to the second attribute
    clusters. This indicates the presences of three product families within the product portfolio,
    each with a distinct set of attributes that characterize their functionality and design.
