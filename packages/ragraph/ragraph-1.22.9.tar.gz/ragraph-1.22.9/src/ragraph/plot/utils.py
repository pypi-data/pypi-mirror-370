"""RaGraph plot utilities."""

from typing import Dict, Iterable, List, Optional, Union

from plotly import graph_objects as go
from plotly.subplots import make_subplots

from ragraph.analysis.sequence._axis import get_axis_sequence  # noqa
from ragraph.edge import Edge
from ragraph.node import Node
from ragraph.plot.components.blank import Blank
from ragraph.plot.components.labels import Labels
from ragraph.plot.components.legend import Legend
from ragraph.plot.components.piemap import PieMap
from ragraph.plot.components.tree import Tree
from ragraph.plot.generic import Component, Style


def get_subplots(components: List[List[Optional[Component]]], style: Style = Style()) -> go.Figure:
    """Get a subplots [`plotly.graph_objects.Figure`][plotly.graph_objects.Figure] for the given
    components list of lists.

    Arguments:
        components: Components to be laid out as subplots based on their width and height
            properties.
        style: Style options.
    """
    rows = len(components)

    components_t = list(zip(*components))  # Transpose helper matrix.
    cols = len(components_t)

    min_x_ranges = [
        (
            min(
                [comp.xaxis.range[0] for comp in col if comp and comp.xaxis.range],
                default=0,
            )
            if any(col)
            else 0
        )
        for col in components_t
        if components_t
    ]

    max_x_ranges = [
        (
            max(
                [comp.xaxis.range[1] for comp in col if comp and comp.xaxis.range],
                default=1,
            )
            if any(col)
            else 1
        )
        for col in components_t
    ]

    widths = [(x_max - x_min) * style.boxsize for (x_max, x_min) in zip(max_x_ranges, min_x_ranges)]

    min_y_ranges = [
        (
            min(
                [comp.yaxis.range[0] for comp in row if comp and comp.yaxis.range],
                default=0,
            )
            if any(row)
            else 0
        )
        for row in components
    ]

    max_y_ranges = [
        (
            max(
                [comp.yaxis.range[1] for comp in row if comp and comp.yaxis.range],
                default=1,
            )
            if any(row)
            else 1
        )
        for row in components
    ]

    heights = [
        (y_max - y_min) * style.boxsize for (y_max, y_min) in zip(max_y_ranges, min_y_ranges)
    ]

    fig = make_subplots(
        rows=rows,
        cols=cols,
        shared_xaxes=True,
        shared_yaxes=True,
        horizontal_spacing=0,
        vertical_spacing=0,
        column_widths=None if sum(widths) == 0 else widths,
        row_heights=None if sum(heights) == 0 else heights,
    )
    fig.layout.update(style.layout)

    shapes, annotations = [], []
    for i, row in enumerate(components):
        y = "y" if i == 0 else f"y{i*cols+1}"
        for j, component in enumerate(row):
            if not component:
                component = Blank()

            x = "x" if i + j == 0 else f"x{j+1+i*cols}"

            # Add traces.
            for trace in component.traces:
                fig.add_trace(trace, i + 1, j + 1)

            # Set shapes' reference axis
            for shape in component.shapes:
                shape.update({"xref": x, "yref": y})

            # Add annotations.
            for annotation in component.annotations:
                annotation.update({"xref": x, "yref": y})

            shapes.extend(component.shapes)
            annotations.extend(component.annotations)

            component.xaxis.update(range=(min_x_ranges[j], max_x_ranges[j]))
            component.yaxis.update(range=(min_y_ranges[i], max_y_ranges[i]))

            component.width = widths[j]
            component.height = heights[i]

            # Axis overrides
            fig.update_xaxes(row=i + 1, col=j + 1, patch=component.xaxis)
            fig.update_yaxes(row=i + 1, col=j + 1, patch=component.yaxis)

    fig.layout.shapes = shapes
    fig.layout.annotations = annotations

    margin = style.layout.margin
    fig.layout.update(
        {
            "width": sum(widths) + margin["l"] + margin["r"],
            "height": sum(heights) + margin["t"] + margin["b"],
        }
    )

    return fig


def process_fig(fig: go.Figure, style: Style = Style(), show: bool = True) -> Optional[go.Figure]:
    """Show figure with config if `show` is set, otherwise return figure unchanged.

    Arguments:
        fig: Plotly figure.
        style: Style containing additional config.
        show: Whether to show the figure inline.
    """
    if show:
        style.config["toImageButtonOptions"] = dict(
            format="svg",
            filename="ragraph_plot",
            width=fig.layout.width,
            height=fig.layout.height,
            margin=dict(l=0, t=0, r=0, b=0),
        )
        fig.show(config=style.config)
        return None
    else:
        return fig


def get_mdm_grid(
    leafs: List[Node], edges: List[Edge], style: Style = Style()
) -> List[List[Optional[Component]]]:
    """Get grid layout for mdm figure.

    Arguments
        leafs: List of nodes to be displayed.
        edges: The edges to be displayed.
        style: Plot style option mapping.

    Returns
        Grid of go.Figure objects.
    """
    col_number_row: List[Optional[Component]] = []
    piemap_row: List[Optional[Component]] = []
    grid: List[List[Optional[Component]]] = []

    if style.row_col_numbers:
        style.labels.textorientation = "vertical"
        col_number_row = [
            None,
            None,
            None,
            Labels([Node(str(i + 1)) for i in range(len(leafs))], style=style),
        ]

        style.labels.textorientation = "horizontal"
        piemap_row = [
            Tree(leafs, style=style),
            Labels(leafs, style=style),
            Labels([Node(str(i + 1)) for i in range(len(leafs))], style=style),
            PieMap(rows=leafs, cols=leafs, edges=edges, style=style),
        ]
    else:
        piemap_row = [
            Tree(leafs, style=style),
            Labels(leafs, style=style),
            PieMap(rows=leafs, cols=leafs, edges=edges, style=style),
        ]

    if style.show_legend and edges:
        if col_number_row:
            col_number_row.append(None)
        piemap_row.append(Legend(edges, style=style))

    if col_number_row:
        grid.append(col_number_row)
    grid.append(piemap_row)

    return grid


def get_dmm_grid(
    rows: List[Node], cols: List[Node], edges: List[Edge], style: Style = Style()
) -> List[List[Union[go.Figure, None]]]:
    """Get grid layout for mdm figure.

    Arguments
        rows: The nodes to be placed on the rows of the matrix.
        cols: The columns to be placed on the columns of the matrix.
        edges: The edges to be displayed.
        style: Plot style option mapping.

    Returns
        Grid of go.Figure objects.
    """
    grid: List[List[Optional[Component]]] = []
    col_num_row: List[Optional[Component]] = []
    col_label_row: List[Optional[Component]] = []
    piemap_row: List[Optional[Component]] = []
    if style.row_col_numbers:
        style.labels.textorientation = "vertical"
        col_label_row = [
            None,
            None,
            Labels(cols, style=style),
        ]
        col_num_row = [
            None,
            None,
            Labels([Node(str(i + 1)) for i in range(len(cols))], style=style),
        ]

        style.labels.textorientation = "horizontal"
        piemap_row = [
            Labels(rows, style=style),
            Labels([Node(str(i + 1)) for i in range(len(rows))], style=style),
            PieMap(rows=rows, cols=cols, edges=edges, style=style),
        ]
    else:
        style.labels.textorientation = "vertical"
        col_label_row = [None, Labels(cols, style=style)]

        style.labels.textorientation = "horizontal"
        piemap_row = [
            Labels(rows, style=style),
            PieMap(rows=rows, cols=cols, edges=edges, style=style),
        ]

    if style.show_legend and edges:
        col_label_row.append(None)
        if col_num_row:
            col_num_row.append(None)
        piemap_row.append(Legend(edges, style=style))

    grid.append(col_label_row)
    if col_num_row:
        grid.append(col_num_row)
    grid.append(piemap_row)

    return grid


def get_swatchplot(*args: Iterable[List[str]], **kwargs: Dict[str, List[str]]) -> go.Figure:
    """Swatch plot of colormaps.

    Arguments:
        *args: Hex coded color lists.
        **kwargs: Names to hex coded color lists.

    Returns:
        Plotly figure.
    """
    colormaps = kwargs
    for i, colormap in enumerate(args):
        colormaps[str(i)] = colormap
    bars = [
        go.Bar(
            orientation="h",
            y=[name] * len(colors),
            x=[1] * len(colors),
            customdata=list(range(len(colors))),
            marker=dict(color=colors),
            hovertemplate="%{y}[%{customdata}] = %{marker.color}<extra></extra>",
        )
        for name, colors in colormaps.items()
    ]

    fig = go.Figure(
        data=bars[::-1],
        layout=dict(
            barmode="stack",
            barnorm="fraction",
            bargap=0.5,
            showlegend=False,
            xaxis=dict(range=[-0.02, 1.02], showticklabels=False, showgrid=False),
            height=max(600, 40 * len(colormaps)),
            margin=dict(b=10),
        ),
    )

    return fig
