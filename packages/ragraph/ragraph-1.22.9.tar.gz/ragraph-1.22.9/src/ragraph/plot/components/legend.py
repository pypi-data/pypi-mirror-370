"""# Legend plot component"""

from collections import defaultdict
from copy import deepcopy
from typing import List

import plotly.graph_objs as go

from ragraph.edge import Edge
from ragraph.plot.generic import Component, Style


class Legend(Component):
    """Legend component.

    Arguments:
        edges: List displayed edges.
        style: Plot style mapping.
    """

    def __init__(self, edges: List[Edge], style: Style = Style()):
        if style.piemap.display in ["kinds", "labels", "weight labels"]:
            # create categorical legend:
            categories = style.piemap.fields or get_legend_categories(
                edges=edges, display=style.piemap.display
            )

            max_label_length = max(len(cat) for cat in categories) if categories else 0
            fontsize = (
                int(0.6 * style.boxsize) if style.legend.fontsize is None else style.legend.fontsize
            )
            width = (
                max_label_length * fontsize * style.legend.fontaspectratio + 1 * style.boxsize
            )  # Text width plus 2 box sizes as margin.

            traces = get_categorical_legend_traces(categories=categories, style=style)
            xaxis, yaxis = deepcopy(style.legend.xaxis), deepcopy(style.legend.yaxis)
            num = len(categories)
            xaxis.update(
                range=[0, (width / style.boxsize) * style.xstep],
            )
            yaxis.update(
                range=[0, (num + 1) * style.ystep],
            )

            super().__init__(
                width=width,
                height=num * style.ystep * style.boxsize,
                traces=traces,
                shapes=None,
                xaxis=xaxis,
                yaxis=yaxis,
            )

        elif style.piemap.display == "weights":
            # Create numerical legend.
            traces = get_numerical_legend_traces(edges=edges, style=style)
            xaxis, yaxis = deepcopy(style.legend.xaxis), deepcopy(style.legend.yaxis)

            weight_labels = style.piemap.fields or get_legend_categories(
                edges=edges, display="weight labels"
            )

            max_label_length = max(len(label) for label in weight_labels) if weight_labels else 0

            fontsize = (
                int(0.6 * style.boxsize) if style.legend.fontsize is None else style.legend.fontsize
            )

            width = 2.5 * style.xstep * len(weight_labels) * style.boxsize
            xaxis.update(
                range=[0, width / style.boxsize * style.xstep],
                scaleanchor="y",
                scaleratio=1.0,
            )
            yaxis.update(range=[0, (style.legend.height) * style.ystep])

            super().__init__(
                width=width,
                height=(style.legend.height) * style.boxsize,
                traces=traces,
                shapes=None,
                xaxis=xaxis,
                yaxis=yaxis,
            )


def get_categorical_legend_traces(
    categories: List[str], style: Style = Style()
) -> List[go.Scatter]:
    """Create categorical legend traces.

    Arguments:
        categories: List of categories.
        style: Plot style mapping.

    Returns:
        List of traces.
    """
    traces = []
    x0 = 0.5
    y0 = (len(categories) - 0.5) * style.ystep

    xdata = []
    ydata = []

    fontsize = int(0.6 * style.boxsize) if style.legend.fontsize is None else style.legend.fontsize

    for idx, cat in enumerate(categories):
        y = y0 - idx * style.ystep
        color = style.palettes.get_categorical_color(idx, field=cat)
        traces.append(
            go.Scatter(
                x=[x0],
                y=[y],
                text=[cat],
                mode="markers",
                marker=dict(color=color),
                hoverinfo="text",
                showlegend=False,
            )
        )

        xdata.append(x0 + 0.5 * style.xstep)
        ydata.append(y)

    traces.append(
        go.Scatter(
            x=xdata,
            y=ydata,
            text=categories,
            hoverinfo="text",
            mode="text",
            showlegend=False,
            textfont=dict(
                color=style.legend.fontcolor,
                family=style.legend.fontfamily,
                size=fontsize,
            ),
            textposition="middle right",
        )
    )

    return traces


def get_swatchtraces(
    idx: int,
    name: str,
    colors: List[str],
    min_value: float,
    max_value: float,
    style: Style = Style(),
) -> List[go.Scatter]:
    """Swatch bar of color map.

    Arguments:
        idx: Number of the swatch that must be created.
        name: name of the swatch trace.
        colors: List of colors to be added to the swatch trace
        min_value: Minimum value of the weight related to the color map.
        max_value: Maximmum value of the weight related to the color map.
        style: Style object.

    Returns:
        List of go.Scatter traces.
    """
    if style.legend.n_ticks < 2:
        x = (1.8 * idx + 0.75) * style.xstep
    else:
        x = (2.5 * idx + 0.75) * style.xstep

    ystep = style.legend.height * style.ystep / len(colors)
    traces = []

    for idc, color in enumerate(colors):
        x0 = x - 0.35 * style.xstep
        x1 = x + 0.35 * style.xstep
        xdata = [x0, x0, x1, x1]

        y0 = style.ystep + (idc) * ystep
        y1 = style.ystep + (idc + 1) * ystep
        ydata = [y0, y1, y1, y0]

        traces.append(
            go.Scatter(
                x=xdata,
                y=ydata,
                fill="toself",
                text=[name for x in xdata],
                mode="lines",
                hoverinfo="text",
                marker=dict(size=0),
                fillcolor=color,
                line=dict(color=color),
                showlegend=False,
            )
        )

    fontsize = int(0.6 * style.boxsize) if style.legend.fontsize is None else style.legend.fontsize

    if style.legend.n_ticks >= 2:
        n = style.legend.n_ticks
        tick_step = (max_value - min_value) / (n - 1)
        traces.append(
            go.Scatter(
                x=[x + 0.5 * style.xstep for step in range(n)],
                y=[style.ystep + step * style.legend.height / (n - 1) for step in range(n)],
                text=["{:.1f}".format(min_value + step * tick_step) for step in range(n)],
                showlegend=False,
                mode="text",
                textfont=dict(
                    color=style.legend.fontcolor,
                    family=style.legend.fontfamily,
                    size=0.7 * fontsize,
                ),
                hoverinfo="text",
                textposition="middle right",
            )
        )

    traces.append(
        go.Scatter(
            x=[x],
            y=[0.5 * style.ystep],
            mode="text",
            text=[name[0:3] + "."],
            showlegend=False,
            textfont=dict(
                color=style.legend.fontcolor,
                family=style.legend.fontfamily,
                size=fontsize,
            ),
            hoverinfo="text",
        )
    )
    return traces


def get_numerical_legend_traces(edges: List[Edge], style: Style = Style()) -> List[go.Scatter]:
    """Get traces for a numerical legend,

    Arguments:
        edges: List of edges that are displayed.
        style: Style object.

    Returns:
       List of traces.
    """
    weight_labels = style.piemap.fields or get_legend_categories(
        edges=edges, display="weight labels"
    )

    traces = []
    for idx, label in enumerate(weight_labels):
        colors = style.palettes.get_continuous_palette(label)
        edge_dict = defaultdict(list)
        for e in edges:
            if e.weights.get(label, None):
                edge_dict[e.source, e.target].append(e.weights[label])

        values = [sum(weights) for weights in edge_dict.values()]
        min_value = min(values, default=0)
        max_value = max(values, default=0)
        if min_value == max_value:
            min_value = max_value - 1

        traces.extend(
            get_swatchtraces(
                idx=idx,
                name=label,
                colors=colors,
                min_value=min_value,
                max_value=max_value,
                style=style,
            )
        )

    return traces


def get_legend_categories(edges: List[Edge], display: str) -> List[str]:
    """Get the number of categories to be included in the legend.

    Arguments:
        edges: The list of edges that are being displayed.
        display: The selected display mode.

    Returns:
        list of categories.
    """
    if display == "kinds":
        return sorted(list(set([e.kind for e in edges])))
    elif display == "labels":
        labels = set()
        for e in edges:
            labels.update(set(e.labels))
        return sorted(list(labels))
    elif display == "weight labels":
        weight_labels = set()
        for e in edges:
            weight_labels.update(set([w for w in e.weights]))
        return sorted(list(weight_labels))
    else:
        return []
