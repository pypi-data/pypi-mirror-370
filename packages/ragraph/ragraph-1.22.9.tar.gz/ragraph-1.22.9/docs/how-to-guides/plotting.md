# Plotting

This page covers plotting [the `Graph` object][ragraph.graph.Graph] in various matrix forms using
[the `ragraph.plot` module][ragraph.plot]. In particular we will focus on [the `ragraph.plot.mdm`
function][ragraph.plot.mdm] and [the `ragraph.plot.Style` object][ragraph.plot.Style]. The
[`mdm`][ragraph.plot.mdm] function can be used to quickly generate multi-domain-matrix (MDM) and
dependency-structure-matrix (DSM) figures of your data set. The [`Style`][ragraph.plot.Style] object
allows one to filter the information to be displayed and set the appearance of the figure.

The [Ford Climate Control System dataset][ragraph.datasets.climate_control] is used to illustrate
the various plot options.

## Basic plotting

To create a plot, first the import the module and use the plot function as follows:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")
fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
)
fig.write_image("docs/generated/mdm_edge_kinds.svg")
```

The [`mdm` function][ragraph.plot.mdm] requires two arguments: `leafs`, which is the list of nodes
to be displayed on the rows and columns of the matrix, and `edges`, which is the list of edges
(dependencies) to be displayed within the matrix. The figure can be saved to file using the
`fig.write_image(filename)` function by Plotly.

The figure below shows the resulting matrix. By default, the different edge kinds are displayed
within the matrix. In this case, the dataset only contains the edge kind `edge`, as shown within the
legend at the bottom right of the figure.

<figure markdown>
![Product DSM of the climate control system showing dependency
kinds.](../generated/mdm_edge_kinds.svg)
<figcaption>
Product DSM of the climate control system showing dependencykinds.
</figcaption>
</figure>

Note that the `leafs` are automatically sorted following the hierarchical structure found within the
graph. If one would like to display the `leafs` within the order as provided, one can pass along the
argument `sort=False` to [the `mdm` function][ragraph.plot.mdm].

In case one wants to create a non-square matrix or a matrix with different nodes on the rows than on
the columns. One can use [the Domain Mapping Matrix `ragraph.plot.dmm` function][ragraph.plot.dmm]:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")
rows = g.leafs[0:6]
cols = g.leafs

fig = plot.dmm(
    rows=rows,
    cols=cols,
    edges=[e for e in g.edges_between_all(sources=cols, targets=rows)],
    sort=False,
)
fig.write_image("./docs/generated/dmm_example.svg")
```

This results in the figure below, in which we now have more columns than rows.

<figure markdown>
![Mapping matrix of the climate control system.](../generated/dmm_example.svg)
<figcaption>
Mapping matrix of the climate control system.
</figcaption>
</figure>

## Tuning the axis nodes

A big part of your figures content is the ordering of leaf nodes on the axis. By default the leaf
nodes you provide will be sorted according to:

1.  The hierarchy they are subject to.
2.  The node kind they belong to.
3.  Whether or not they are a bus node.
4.  How big their "width" is in terms of leaf nodes (e.g. biggest clusters first).

You can tweak this behavior like so:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    node_kinds=["node"],  # You can order and filter node kinds here.
    sort_args=dict(
        sort_by_bus=False,  # Don't actively put bus nodes first.
        sort_by_width=False,  # Don't put wider (larger) nodes first.
    ),
)
fig.write_image('./docs/generated/mdm_tweaked_sort.svg')
```

<figure markdown>
![MDM figure with automatic sorting tweaked to only reflect the hierarchy and no further
optimizations.](../generated/mdm_tweaked_sort.svg)
<figcaption>
MDM figure with automatic sorting tweaked to only reflect the hierarchy and no further
optimizations.
</figcaption>
</figure>

Where `sort_args` are options to be passed to
[`ragraph.analysis.sequence.axis`][ragraph.analysis.sequence.axis].

Or you can also disable this behavior altogether and plot the (leaf) nodes as given:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,  # Custom ordering here.
    edges=g.edges,
    sort=False,
)
fig.write_image("./docs/generated/mdm_custom_sort.svg")
```

<figure markdown>
![MDM figure with automatic sorting disabled. Sorting is fully custom as given in the leaf
list.](../generated/mdm_custom_sort.svg)
<figcaption>
MDM figure with automatic sorting disabled. Sorting is fully custom as given in the leaf
list.
</figcaption>
</figure>

## Information filtering

The [`Graph`][ragraph.graph.Graph] may contain [`Edge`][ragraph.edge.Edge] objects of various kinds
to which various labels and weights are attached. By passing along a [`Style`][ragraph.plot.Style]
object to the `style` argument of the [`mdm`][ragraph.plot.mdm] function one can set the information
that is displayed within the matrix.

In the snippet below, the value of the `display` key of the `piemap` property of the
[`Style`][ragraph.plot.Style] object is set to be equal to `"weight labels"`.

The snippet and corresponding figure below show the resulting matrix in which the labels of the
different weights attached to the edges are displayed as categories within a pie chart.

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(piemap=dict(display="weight labels")),
)
fig.write_image("./docs/generated/mdm_edge_weight_labels.svg")
```

<figure markdown>
![Product DSM of the climate control system showing all edge weight
labels.](../generated/mdm_edge_weight_labels.svg)
<figcaption>
Product DSM of the climate control system showing all edge weight
labels.
</figcaption>
</figure>

By changing the value of `display` to `"weights"` the matrix changes from a categorical plot to a
numerical plot as shown in the next figure. Here the actual numerical values of the different
weights are shown rather than the weight labels.

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
        )
    ),
)
fig.write_image("./docs/generated/mdm_edge_weights_1.svg")
```

<figure markdown>
![Product DSM of the climate control system showing edge
weights.](../generated/mdm_edge_weights_1.svg)
<figcaption>
Product DSM of the climate control system showing edge weights.
</figcaption>
</figure>

By default, all elements that belong to the `display` category are shown. One can change this by
setting the `fields` key of the `piemap` dictionary as shown in the following snippet, which yields
the figure right after it. Here only the numerical values of the weights `"spatial"`, `"energy
flow"`, and `"information flow"` are displayed.

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=[
                "spatial",
                "energy flow",
                "information flow",
            ],
        )
    ),
)
fig.write_image("./docs/generated/mdm_edge_weights_2.svg")
```

<figure markdown>
![Product DSM of the climate control system showing a subset of edge
weights.](../generated/mdm_edge_weights_2.svg)
<figcaption>
Product DSM of the climate control system showing a subset of edge weights.
</figcaption>
</figure>

In all figures shown so far, the wedges displayed within the pie charts are of equal size. You can
change this by setting the value of the `mode` key of the `piemap` dictionary to `"relative"`. As a
result, the size of the wedges is scaled following the numerical value attached to it as shown in
the following:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=[
                "spatial",
                "energy flow",
                "information flow",
            ],
            mode="relative",
        )
    ),
)
fig.write_image("./docs/generated/mdm_edge_weights_3.svg")
```

<figure markdown>
![Product DSM of the climate control system showing relative wedge
sizes.](../generated/mdm_edge_weights_3.svg)
<figcaption>
Product DSM of the climate control system showing relative wedge sizes.
</figcaption>
</figure>

The examples shown in this section are far from exhaustive. Check out the
[`ragraph.plot.generic.PieMapStyle`][ragraph.plot.generic.PieMapStyle] documentation for all
properties that one can set within the `piemap` dictionary.

## Information highlighting

Highlighting certain rows and columns is possible as well. By default, you can highlight rows and
columns by setting the `highlight` annotation to `True` on a [`Node`][ragraph.node.Node] instance:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

g["Accumulator"].annotations.highlight = True
g["Compressor"].annotations.highlight = "rgba(255,0,0,0.25)"

fig = plot.mdm(leafs=g.leafs, edges=g.edges)
fig.write_image("./docs/generated/mdm_highlight.svg")
```

<figure markdown>
![Product DSM of the climate control system highlighting the
Accumulator.](../generated/mdm_highlight.svg)
<figcaption>
Product DSM of the climate control system highlighting the Accumulator and Compressor.
</figcaption>
</figure>

You can override certain settings via [the `Style` object][ragraph.plot.Style], too:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

style = plot.Style(
    highlight_annotation="highlight",
    highlight_color="rgba(0,255,0,0.5)",
    piemap=dict(
        highlight_row_annotation="row",
        highlight_row_color="rgba(255,0,0,0.5)",
        highlight_col_annotation=None,
        highlight_col_color=None,
    ),
)

g["Accumulator"].annotations.row = "rgba(0,0,255,0.25)"
g["Command Distribution"].annotations.row = True
g["Compressor"].annotations.highlight = True

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=style,
)
fig.write_image("./docs/generated/mdm_highlight_custom.svg")
```

<figure markdown>
![Product DSM of the climate control system showcasing all highlighting
options.](../generated/mdm_highlight_custom.svg)
<figcaption>
Product DSM of the climate control system showcasing all highlighting options.
</figcaption>
</figure>

That's a lot of overrides fighting for precedence! In short, when you override the
`highlight_row_annotation` or `highlight_col_annotation` keys in the piemap specific options, the
PieMap's highlighting of rows or columns will only look for those annotation keys in row or column
Nodes (e.g. the default one is completely ignored). If these override are unset or `None`, it will
look for the global highlight annotation key. So:

1. [`ragraph.plot.generic.PieMapStyle`][ragraph.plot.generic.PieMapStyle]'s row/column annotation
   key is considered.
1. Only if there is no style entry for that, the
   [`ragraph.plot.generic.Style`][ragraph.plot.generic.Style] highlight key is considered.

Secondly, the color's precedence is always:

1. Annotation key's value if it's a string.
1. [`ragraph.plot.generic.PieMapStyle`][ragraph.plot.generic.PieMapStyle] row/column override color
   if set.
1. [`ragraph.plot.generic.Style`][ragraph.plot.generic.Style] default highlight color.

## Matrix styling

The colors of the fields displayed within the matrix are automatically generated. However, for easy
comparison of multiple plots one may want to explicitly set the color, or color map of a field.

In the snippet below the the color of the displayed weight labels are explicitly set by setting the
value of the `fields` key within the `palettes` property of the [`Style`][ragraph.plot.Style]
object. Here one can provide a dictionary mapping `weight labels` to `color hex codes`. The result
of setting these colors is shown in the following snippet and figure:

```python
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(
        piemap=dict(
            display="weight labels",
            fields=[
                "spatial",
                "energy flow",
                "information flow",
                "material flow",
            ],
        ),
        palettes=dict(
            fields={
                "spatial": {"categorical": "#a64747"},
                "energy flow": {"categorical": "#de9c38"},
                "information flow": {"categorical": "#148a8e"},
                "material flow": {"categorical": "#b8bd6c"},
            }
        ),
    ),
)
fig.write_image("./docs/generated/mdm_edge_categorical_field_colors.svg")
```

<figure markdown>
![Product DSM of the climate control system showing edge weight labels with user defined
colors.](../generated/mdm_edge_categorical_field_colors.svg)
<figcaption>
Product DSM of the climate control system showing edge weight labels with user defined colors.
</figcaption>
</figure>

Similarly, one can set the colors for numerical values. Here one has to provide a list of colors (a
color map). [The `ragraph.colors` module][ragraph.colors] provides several functions for generating
such color maps.

In the example below, the functions `get_diverging_redblue`, `get_diverging_orangecyan`, and
`get_diverging_purplegreen` are used to set a diverging color map for the displayed weights in the
next figure.

```python
from ragraph import datasets, plot
from ragraph.colors import (
    get_diverging_redblue,
    get_diverging_orangecyan,
    get_diverging_purplegreen,
)

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(
        piemap=dict(
            display="weights",
            fields=[
                "spatial",
                "energy flow",
                "information flow",
            ],
        ),
        palettes=dict(
            fields={
                "spatial": {"continuous": get_diverging_redblue()},
                "energy flow": {"continuous": get_diverging_orangecyan()},
                "information flow": {"continuous": get_diverging_purplegreen()},
            }
        ),
    ),
)
fig.write_image("./docs/generated/mdm_edge_continuous_field_colors.svg")
```

<figure markdown>
![Product DSM of the climate control system showing edge weight labels with user defined color
gradients.](../generated/mdm_edge_continuous_field_colors.svg)
<figcaption>
Product DSM of the climate control system showing edge weight labels with user defined color gradients.
</figcaption>
</figure>

Check out the documentation of the [`ragraph.plot.generic.Palettes`][ragraph.plot.generic.Palettes]
object to check all options that can be set using the `pallettes` argument.

## Basic customization

The DSM literature presents a create variety of matrix based visualizations. These visualizations
often differ with respect to the information displayed within the matrix. The [`ragraph.plot`
module][ragraph.plot] is built upon the open source [Plotly](https://plotly.com/python/) library. As
such, one can customize the generated figures.

In the snippet below numbers and squares are added to the diagonal of the matrix. The numbers are
added by adding a scatter trace to the figure using the `add_trace` method.

```python
import plotly.graph_objs as go
from ragraph.colors import get_green
from ragraph import datasets, plot

g = datasets.get("climate_control")

fig = plot.mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=plot.Style(piemap=dict(display="kinds")),
)
# Coordinates and colors for custom traces and shapes.
n_nodes = len(g.leafs)
x = [idx + 0.5 for idx in range(n_nodes)]
y = [n_nodes - 0.5 - idy for idy in range(n_nodes)]
colors = get_green(n_nodes)
# Create and add trace for numbers on diagonal.
text_trace = go.Scatter(
    x=x,
    y=y,
    text=[str(idx + 1) for idx in range(n_nodes)],
    mode="text",
    showlegend=False,
)
fig = fig.add_trace(text_trace, row=2, col=4)
# Create and add shapes for colored squares on diagonal.
shapes = []
for idx, color in enumerate(colors):
    shapes.append(
        go.layout.Shape(
            type="rect",
            x0=x[idx] - 0.5,
            y0=y[idx] + 0.5,
            x1=x[idx] + 0.5,
            y1=y[idx] - 0.5,
            fillcolor=color,
            xref="x9",
            yref="y9",
            layer="below",
        )
    )
fig = fig.update_layout(shapes=list(fig.layout.shapes) + shapes)
fig.write_image("./docs/generated/mdm_custom.svg")
```

<figure markdown>
![Product DSM of the climate control system showing edge kinds with a custom color gradient and
numbers on the diagonal.](../generated/mdm_custom.svg)
<figcaption>
Product DSM of the climate control system showing edge kinds with a custom color gradient and
numbers on the diagonal.
</figcaption>
</figure>

Note the `row` and `col` arguments of the `add_trace` method. The plot consists of six components
which are instances of the [`Tree`][ragraph.plot.components.Tree],
[`Labels`][ragraph.plot.components.Labels], [`PieMap`][ragraph.plot.components.PieMap], and
[`Legend`][ragraph.plot.components.Legend] objects. These components are placed within a grid
containing two rows and five columns. By setting the `row` and `col` arguments one can add the trace
to one of the six plot components.

The squares are added by using the `update_layout` method to update the `shapes` property of the
figure. In creating the figure shapes, the arguments `xref` and `yref` are set to `x9` and `y9`,
respectively. This ensures that the shapes are positioned with respect to x-axis nine and y-axis
nine. In this case, being the axes of the matrix (piemap).

## Advanced customization

One can take customization one step further. As the plot components are placed within a grid, one
can expand the grid with additional rows and columns filled with custom components.

The snippet below shows a custom plot component class `ColorBar`, which inherits its properties from
the [`ragraph.plot.generic.Component`][ragraph.plot.generic.Component] class which is the basic
building block for creating compound Plotly figures.

```python
from ragraph import datasets
from ragraph.plot.generic import Component, Style
from ragraph.node import Node
from ragraph.edge import Edge
from ragraph.plot import utils, components
from ragraph.colors import (
    get_red,
    get_green,
    get_orange,
    get_blue,
)
from plotly import graph_objs as go
from typing import List, Optional


class ColorBar(Component):
    """Color bar plot component.
    Arguments:
      leafs: The list of nodes on the axis of the matrix.
      colors: The list of colors to be used in the color bar
              (len(colors >= len(leafs))).
      orientation: One of "horizontal" or "vertical". Defaults to vertical
      Style: Style object of the plot.
    """

    def __init__(
        self,
        leafs: List[Node],
        colors: List[str],
        orientation: str = "vertical",
        style: Style = Style(),
    ):
        # Calculating shape coordinates
        shapes = []
        for idx in range(len(leafs)):
            if orientation == "vertical":
                x0 = 0
                x1 = style.xstep
                y0 = idx * style.ystep
                y1 = (idx + 1) * style.ystep
            elif orientation == "horizontal":
                x0 = idx * style.xstep
                x1 = (idx + 1) * style.xstep
                y0 = 0
                y1 = style.ystep
            shapes.append(
                go.layout.Shape(
                    type="rect",
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    fillcolor=colors[idx],
                )
            )
        # Calculating geometric boundaries.
        if orientation == "vertical":
            width = (style.xstep) * style.boxsize
            height = len(leafs) * style.ystep * style.boxsize
        elif orientation == "horizontal":
            width = len(leafs) * style.xstep * style.boxsize
            height = (style.ystep) * style.boxsize
        xaxis = go.layout.XAxis(
            automargin=False,
            scaleanchor="y",
            autorange=False,
            scaleratio=1.0,
            # showgrid=True,
            # showline=True,
            showticklabels=False,
            # zeroline=True,
            range=(0, width / style.boxsize),
        )
        yaxis = go.layout.YAxis(
            automargin=False,
            autorange=False,
            showgrid=True,
            # showline=True,
            showticklabels=False,
            # zeroline=True,
            range=(0, height / style.boxsize),
        )
        super().__init__(
            width=width,
            height=height,
            traces=[],
            shapes=shapes,
            xaxis=xaxis,
            yaxis=yaxis,
        )


def custom_mdm(
    leafs: List[Node],
    edges: List[Edge],
    style: Style = Style(),
    sort: Optional[bool] = True,
    node_kinds: Optional[List[str]] = None,
    show: Optional[bool] = False,
) -> go.Figure:
    """Get a custom plot of a Graph object."""
    if sort:
        leafs = utils.get_axis_sequence(leafs, kinds=node_kinds)
    first_row = [
        None,
        None,
        None,
        ColorBar(
            leafs=leafs,
            colors=get_red(len(leafs)),
            orientation="horizontal",
            style=style,
        ),
        None,
        None,
    ]
    second_row = [
        components.Tree(leafs, style=style),
        components.Labels(leafs, style=style),
        ColorBar(
            leafs=leafs,
            colors=get_green(len(leafs)),
            orientation="vertical",
            style=style,
        ),
        components.PieMap(rows=leafs, cols=leafs, edges=edges, style=style),
        ColorBar(
            leafs=leafs,
            colors=get_orange(len(leafs)),
            orientation="vertical",
            style=style,
        ),
        components.Legend(edges, style=style),
    ]
    third_row = [
        None,
        None,
        None,
        ColorBar(
            leafs=leafs,
            colors=get_blue(len(leafs)),
            orientation="horizontal",
            style=style,
        ),
        None,
        None,
    ]
    fig = utils.get_subplots([first_row, second_row, third_row])
    return utils.process_fig(fig=fig, show=show, style=style)


g = datasets.get("climate_control")
fig = custom_mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=Style(
        piemap=dict(display="weight labels"),
    ),
)
fig.write_image("./docs/generated/mdm_custom_advanced.svg")
```

<figure markdown>
![Product DSM of the climate control system showing edge weights labels with custom colorbars around
the matrix.](../generated/mdm_custom_advanced.svg)
<figcaption>
Product DSM of the climate control system showing edge weights labels with custom colorbars around
the matrix.
</figcaption>
</figure>

The grid layout of this figure was defined within the `custom_mdm` method. The figure is composed of
three rows and six columns. The first row contains a `ColorBar` component within the fourth column.
All other positions are empty within. The second row contains six plot components: a
[`Tree`][ragraph.plot.components.Tree], [`Labels`][ragraph.plot.components.Labels], a custom
`ColorBar`, a [`PieMap`][ragraph.plot.components.PieMap], another `ColorBar`, and a
[`Legend`][ragraph.plot.components.Legend] component. The third row only contains a `ColorBar`
component in the right position.

With use of the functions Ragraph
[`ragraph.plot.utils.get_subplots`][ragraph.plot.utils.get_subplots] and
[`ragraph.plot.utils.process_fig`][ragraph.plot.utils.process_fig] the plot components are joined
into a single Plotly figure object.

!!! note

    Matching the scaling of all figures within a grid plot can be quite tricky. The axis of
    neighboring plots are automatically linked. Hence one should take care when setting the range of
    the axis of custom plot components. The [`Style.xstep`][ragraph.plot.Style.xstep],
    [`Style.ystep`][ragraph.plot.Style.ystep], and [`Style.boxsize`][ragraph.plot.Style.boxsize]
    properties of the [`Style`][ragraph.plot.Style] object are particularly important in matching
    the scaling of figures.

## Edge direction convention

Whilst the example matrix of the climate control system is symmetrical, you might have a directed
graph instead, such as the [`UCAV`][ragraph.datasets.ucav] dataset. By default, we utilize the
IR-FAD convention (Inputs in Rows, Feedback Above the Diagonal). Lets visualize the default first:

```python
from ragraph import datasets
from ragraph.plot import mdm

g = datasets.get("ucav")
fig = mdm(
    leafs=g.leafs,
    edges=g.edges,
)
fig.write_image("./docs/generated/mdm_ucav_ir_fad.svg")
```

<figure markdown>
![Process DSM of the UCAV design project using the default IR-FAD convention.](../generated/mdm_ucav_ir_fad.svg)
<figcaption>
Process DSM of the UCAV design project using the default IR-FAD convention.
</figcaption>
</figure>

If you would like to follow the opposite convention, IC-FBD (Inputs in Columns, Feedback Below the
Diagonal), that is possible using the `convention` property of the
[`Style`][ragraph.plot.generic.Style.convention] object.

```python
from ragraph import datasets
from ragraph.plot import mdm, Style
from ragraph.generic import Convention

g = datasets.get("ucav")
fig = mdm(
    leafs=g.leafs,
    edges=g.edges,
    style=Style(convention=Convention.IC_FBD),
)
fig.write_image("./docs/generated/mdm_ucav_ic_fbd.svg")
```

<figure markdown>
![Process DSM of the UCAV design project using the default IC-FBD convention.](../generated/mdm_ucav_ic_fbd.svg)
<figcaption>
Process DSM of the UCAV design project using the default IC-FBD convention.
</figcaption>
</figure>

## Chord plot

If you'd like to make a chord plot, you can do so, powered by the rachord package!

```python
from ragraph import datasets
from ragraph.plot import chord, Style

g = datasets.get("climate_control")
fig = chord(g, nodes=g.leafs, style=Style(chord=dict()), symmetrize=False)
fig.save_svg("./docs/generated/chord_cc.svg")
```

<figure markdown>
![Chord plot of the Climate Control dataset.](../generated/chord_cc.svg)
<figcaption>
Chord plot of the Climate Control dataset.
</figcaption>
</figure>

Take a look at [`ragraph.plot.chord`][ragraph.plot.chord] or the relevant `chord` style
key that reflects the [`ragraph.plot.generic.ChordStyle`][ragraph.plot.generic.ChordStyle] options.
