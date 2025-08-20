# Comparative analysis

In engineering design it is common practice to compare different architectures. For example, to
highlight the differences or commonalities between two conceptual designs, different generations of
a system, or different products within a portfolio. In the [Delta analysis
section](#delta-analysis), an example is given of an architecture difference analysis. Following
that, an example is given of a commonality study in the [Sigma analysis section](#sigma-analysis).

The [`ragraph.analysis.comparison` module][ragraph.analysis.comparison] is the one powering these
comparative studies. This module includes two main methods, being the
[`ragraph.analysis.comparison.delta_graph`][ragraph.analysis.comparison.delta_graph] and
[`ragraph.analysis.comparison.sigma_graph`][ragraph.analysis.comparison.sigma_graph] methods, that
enable the calculations of differences and summations, respectively.

The examples use datasets that were created as part of the MultiWaterWerken, MultiWaterWorks or MWW
for short, project of the Dutch Ministry of Infrastructure "Rijkswaterstaat". The graphs used here
describe [waterway locks](<https://en.wikipedia.org/wiki/Lock_(water_navigation)>) as components
(nodes) that share interfaces (edges) along which different flows are exchanged (weights range from
0 to 2 max). As an example, the architecture of MWW Lock "Sambeek" is given in `sambeek`, which is
created using the following snippet:

```python
from ragraph import colors, datasets, plot

sambeek = datasets.get("mww_lock_sambeek")
style = plot.Style(
    piemap=dict(display="weights", mode="relative"),
    palettes=dict(
        fields={
            "energy": dict(continuous=colors.get_orange()),
            "information": dict(continuous=colors.get_blue()),
            "location": dict(continuous=colors.get_purple()),
            "spatial": dict(continuous=colors.get_green()),
        }
    ),
)
fig = plot.mdm(leafs=sambeek.leafs, edges=sambeek.edges, style=style)
fig.write_image("./docs/generated/mww_lock_sambeek.svg")
```

<figure markdown>
![System architecture of the MWW lock Sambeek. All MWW datasets include edges with energy,
information, location and spatial weights to denote different interactions over the interfaces
(edges) between components (nodes).](../generated/mww_lock_sambeek.svg)
<figcaption>
    System architecture of the MWW lock Sambeek. All MWW datasets include edges with energy,
    information, location and spatial weights to denote different interactions over the interfaces
    (edges) between components (nodes).
</figcaption>
</figure>

## Delta analysis

The delta analysis, or difference analysis, enables you to highlight the differences between to
graph objects. In this example, the graph objects represent product architectures of waterway
navigation locks. For two given architecture graphs we can then calculate the delta graph to detect
the unique parts (nodes) to each architecture, as well as their commonalities or unchanged parts.

The following snippet calculates a delta graph between the MWW locks _"Sambeek"_ and _"Sluis15"_
with default settings (more on that later). This by default gives us a graph (here named `delta`)
that separates nodes and edges by assigning different values for the `kind` property.

```python
from ragraph import datasets
from ragraph.analysis import comparison

sambeek = datasets.get("mww_lock_sambeek")
sluis15 = datasets.get("mww_lock_sluis15")
delta = comparison.delta_graph(sambeek, sluis15)
assert delta.node_kinds == ["common", "delta_a", "delta_b"]
assert delta.edge_kinds == ["common", "delta_a", "delta_b"]
```

Let's inspect the results some further:

```python
from ragraph import datasets
from ragraph.analysis import comparison

sambeek = datasets.get("mww_lock_sambeek")
sluis15 = datasets.get("mww_lock_sluis15")
delta = comparison.delta_graph(sambeek, sluis15)

# Common nodes.
num_common = len([n for n in delta.nodes if n.kind == "common"])
percentage_common = round(num_common / delta.node_count, 2)
assert percentage_common == 0.86, "Quite a lot in common!"

# A's unique nodes.
num_delta_a = len([n for n in delta.nodes if n.kind == "delta_a"])
percentage_delta_a = round(num_delta_a / delta.node_count, 2)
assert percentage_delta_a == 0.11, "Unique to Sambeek."

# B's unique nodes.
num_delta_b = len([n for n in delta.nodes if n.kind == "delta_b"])
percentage_delta_b = round(num_delta_b / delta.node_count, 2)
assert percentage_delta_b == 0.04, "Unique to Sluis 15."

# Common edges (similarly).
num_common_edges = len([e for e in delta.edges if e.kind == "common"])
assert round(num_common_edges / delta.edge_count, 2) == 0.73, "Unchanged interfaces."
```

While these numbers offer some insight in the amount of change in architecture, they are better
visualized using a MDM. Let's create one!

```python
from ragraph import datasets, plot
from ragraph.analysis import comparison

sambeek = datasets.get("mww_lock_sambeek")
sluis15 = datasets.get("mww_lock_sluis15")
delta = comparison.delta_graph(sambeek, sluis15)

style = plot.Style(piemap=dict(display="kinds", mode="relative"))
fig = plot.mdm(
    leafs=delta.nodes,
    edges=delta.edges,
    style=style,
    node_kinds=["delta_a", "delta_b", "common"],
)
fig.write_image("./docs/generated/mww_delta_sambeek_sluis15.svg")
```

<figure markdown>
![Delta MDM between the architectures of MWW locks Sambeek and Sluis15.
](../generated/mww_delta_sambeek_sluis15.svg)
<figcaption>
Delta MDM between the architectures of MWW locks Sambeek and Sluis15.
</figcaption>
</figure>

In this figure we have plotted the three node kinds in the sequence `["delta_a", "delta_b",
"common"]`. The upper left of the MDM designates the nodes that are unique to the first graph (the
`"a"` graph), followed by the nodes unique to the second graph (the `"b"` graph), and on the bottom
right their common core.

The edges are categorized in the same manner as the nodes using their kind. On, from, and towards
the `"delta_a"` nodes on the top left you will only find edges with a `"delta_a"` kind and the same
holds for the `"delta_b"` nodes and related edges right thereafter. Inside their `"common"` shared
nodes, we can find edges that are also shared between both graphs. A `"common"` edge is an edge that
shares the same source node name, target node name, kind, labels, and weights in the original two
graphs. As soon as any of these properties differ or no counterpart is present, an edge of a
`"delta_a"` or `"delta_b"` kind is added accordingly.

In the figure above, you can find that Sambeek contains 6 elements that Sluis15 does not have versus
two elements the other way around. However, since these components fulfill fairly similar uses
(safety precautions and communication installations), we can see that their interfaces are rather
interchangeable. Their common core shows a very high commonality with regards to their interfaces,
too, although one should not tread lightly over such changes. Especially in case of large moving
components such as the doors, actuators and leveling systems in case of waterway locks.

### Tweaking results

The delta analysis supports various tweaks. The naming of the categories is customizable through the
identically named function arguments to
[`ragraph.analysis.comparison.delta_graph`][ragraph.analysis.comparison.delta_graph]. For instance,
providing `common="shared"` will rename the common node kind to `"shared"`. The `delta_a` and
`delta_b` arguments can be used similarly.

If you wish to store the categorization information in the node or edge labels or annotations
instead of the kinds, you can supply a [`ragraph.analysis.comparison.TagMode] to the `tag_mode`
argument of [`delta_graph`][ragraph.analysis.comparison.delta_graph].

Finally, the uniqueness of nodes and edges is calculated using descriptors, which are abstractions
of both nodes or edges based on a couple of properties. These need to be hashable such that the
delta analysis can make use of set operations to find the unique and shared instances according to
those descriptions. If you wish to implement your own, take a look at the abstract classes
[`ragraph.analysis.comparison.NodeDescriptorLike`][ragraph.analysis.comparison.NodeDescriptorLike]
and
[`ragraph.analysis.comparison.EdgeDescriptorLike`][ragraph.analysis.comparison.EdgeDescriptorLike]
or their default implementations
[`ragraph.analysis.comparison.NodeDescriptor`][ragraph.analysis.comparison.NodeDescriptor] and
[`ragraph.analysis.comparison.EdgeDescriptor`][ragraph.analysis.comparison.EdgeDescriptor].

## Sigma analysis

The sigma analysis excels in portfolio analysis while the [delta_analysis](#delta-analysis) excels
in highlighting the commonalities and differences between two graphs or architectures. When doing an
analysis of larger sets of graphs, it is often easier to distinguish patterns from their sum rather
than their individual differences. These summed graphs can be subjected to weighted clustering
analysis, which aids in identifying modules (clusters) of components (nodes) that predominantly form
the common core of a product portfolio, modules that are optional and modules that are unique.

The MWW lock datasets are plentiful, and therefore we can use those to calculate a sigma graph. The
following snippet calculates a sigma graph for the Eefde, Hansweert, Sambeek, Sluis15 en Volkerak
locks. After that, a baseline figure using some sensible styling is created for further inspection,
which is included further below.

```python
from ragraph import datasets, plot
from ragraph.analysis import comparison

eefde = datasets.get("mww_lock_eefde")
hansweert = datasets.get("mww_lock_hansweert")
sambeek = datasets.get("mww_lock_sambeek")
sluis15 = datasets.get("mww_lock_sluis15")

sigma = comparison.sigma_graph([eefde, hansweert, sambeek, sluis15])
assert sigma.weights["sigma"] == 4, "The absolute count of graphs should be 4."
assert (sigma.node_count, sigma.edge_count) == (
    64,
    490,
), "Check counts"
assert sigma.edge_weight_labels == [
    "energy",
    "information",
    "location",
    "sigma",
    "sigma_label_default",
    "spatial",
]

style = plot.Style(
    piemap=dict(
        display="weights",
        fields=["sigma"],
    )
)
fig = plot.mdm(sigma.leafs, sigma.edges, style=style)
fig.write_image("./docs/generated/mww_sigma.svg")
```

This snippet shows that we now have a summed graph containing 64 nodes and 490 edges, of which the
DSM can be found in the figure below. The sigma graph contains counts as opposed the categories in
the delta analysis and all calculated information is therefore stored into the weights attached to
the graph, nodes, and edges. Weights are introduced for edge occurrence (here seen as `"sigma"`) for
any attached labels (`"sigma_label_default"` for the `"default"` label) and regular weights are
summed, too. With these datasets, we are only interested in the absolute edge counts or their
attached weights, since there is no other information except the default values in them.

<figure markdown>
![Sigma DSM of the architectures of MWW locks Eefde, Hansweert, Sambeek, and Sluis15.
](../generated/mww_sigma.svg)
<figcaption>
    Sigma DSM of the architectures of MWW locks Eefde, Hansweert, Sambeek, and Sluis15.
</figcaption>
</figure>

### Clustering sigma graphs

Sigma graphs are great candidates for a clustering analysis. Such an analysis applied to graphs
representing system architectures aids in identifying modules (clusters) of components (nodes) that
predominantly form the common core of a product portfolio, modules that are optional and modules
that are unique.

With the MWW graphs that are used as an example in this section, we have to make sure we use an
appropriate weight while performing the clustering analysis. The `"sigma"` weight, i.e. the number
of times a certain edge occurred in the individual graphs combined, should give the most predictable
results. If you would be interested in a more mono-disciplinary result, you could use a different
edge weight.

As this is a product architecture dataset, we expect to find a bus module formed by highly
integrative components and several modules with strong interdependencies but relatively little
dependencies between those modules. Therefore, the
[`ragraph.analysis.heuristics.markov_gamma`][ragraph.analysis.heuristics.markov_gamma] seems an
appropriate bus-detection and clustering heuristic to use. The style in the previous paragraph is
re-used here and the resulting figure can be found below.

```python
from ragraph import datasets, plot
from ragraph.analysis import comparison, heuristics

eefde = datasets.get("mww_lock_eefde")
hansweert = datasets.get("mww_lock_hansweert")
sambeek = datasets.get("mww_lock_sambeek")
sluis15 = datasets.get("mww_lock_sluis15")

sigma = comparison.sigma_graph([eefde, hansweert, sambeek, sluis15])

sigma_h, _ = heuristics.markov_gamma(
    sigma,
    alpha=2,
    beta=3.0,
    mu=2.0,
    gamma=2.5,
    inplace=False,
)  # Parameters have been tuned by expert judgment.
style = plot.Style(
    piemap=dict(
        display="weights",
        fields=["sigma"],
    )
)
fig = plot.mdm(sigma.leafs, sigma.edges, style=style)
fig.write_image("./docs/generated/mww_sigma_h.svg")
```

<figure markdown>
![Result of bus detection and clustering applied to the Sigma DSM.
](../generated/mww_sigma_h.svg)
<figcaption>
    Result of bus detection and clustering applied to the Sigma DSM.
</figcaption>
</figure>

In this figure we can observe that the analysis put the main construction components and
installations as the "bus" of the system. From an engineering perspective this is rather
unsurprising. Separating these bus components from the remaining components gives a clearer view in
the remaining modules that are "built on" or "bolted on" the bus.

Furthermore, the layout of a waterway lock is still clearly represented in the clustering. The upper
lock head (_"bovenhoofd"_, abbreviated as `"Bo"`, row 10-15) and lower lock head (_"benedenhoofd"_,
abbreviated as `"Be"`, row 16-20) are still very much grouped together with their doors. This also
holds for the ways into and out of the lock, where you typically find the waiting spaces and
queueing facilities (row 28-40). The power grid utilities are also neatly grouped together in rows
21 to 24, as well as some control components that are related to the lock head (doors).

All combined, this gives an overview of what a _"Superlock"_ would look like. The shade of the given
interfaces represents its occurrence, which gives an insight in the _"essence"_, _"optionality"_, or
even _"rarity"_ of an interface. Very light color shades might indicate opportunities for
deprecation in the future, such that you can simplify your product portfolio. Very dark or clusters
of very darkly shaded interfaces indicate they are omnipresent and are prime candidates for
standardization.

### Engineering judgment

Figures like these are incredibly useful to kickstart your portfolio understanding or discussions
based on numbers instead of gut feeling. However, whilst they can highlight opportunities for
standardization or deprecation of components or interfaces, the engineering judgment whether it is a
good or feasible opportunity to pursue remains quintessential.
