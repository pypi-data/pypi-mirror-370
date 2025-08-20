"""# Piechart mapping matrix plot component

The mapping plot is a matrix of pie-charts, indicating the edges between leaf nodes.

The nodes are identically placed from left-to-right as well as top-to-bottom. This
results in a diagonal (from top-left to bottom-right) of 'self loops', which are
commonly used to indicate "the nodes themselves".

The pie-charts can represent a number of things, including edge weights, edge labels as
well as other metrics. The node hierarchy is included using squares drawn around the
diagonal.

Furthermore, bus nodes have their respective row and column in a shaded background
color. This sets apart the buses' "highly integrative" edges from the regular edges
between nodes.
"""

from collections import OrderedDict, defaultdict
from copy import deepcopy
from math import cos, pi, prod, sin
from typing import Any, Dict, List, Tuple

import plotly.graph_objs as go

from ragraph import colors
from ragraph.edge import Edge
from ragraph.generic import Convention
from ragraph.node import Node
from ragraph.plot import svg
from ragraph.plot.generic import Component, Style


class PieMap(Component):
    """A map of piecharts plot component.

    This map, or matrix, of pie-charts display the edges between leaf nodes.

    Arguments:
        rows: The nodes to be placed on the rows of the matrix.
        cols: The columns to be placed on the columns of the matrix.
        edges: Edges to be displayed between leaf nodes.
        style: Plot style option mapping.

    Note:
        The pie-charts can represent a number of things, including edge weights, edge
        labels as well as other metrics. The node hierarchy is included using squares
        drawn around the diagonal.

        Furthermore, bus nodes have their respective row and column in a shaded
        background color. This sets apart the buses' "highly integrative" edges from the
        regular edges between nodes.

    """

    def __init__(
        self,
        rows: List[Node],
        cols: List[Node],
        edges: List[Edge] = [],
        style: Style = Style(),
        **kwargs,
    ):
        # Custom grid.
        grid_shapes = _get_grid_shapes(rows, cols, style)

        # Display data
        pie_traces, pie_shapes = _get_pies_data(rows, cols, edges, style)

        hierarchy_shapes, kind_shapes = [], []
        if rows == cols:
            # Matrix is symmetric.
            # Shapes to indicate hierarchy.
            hierarchy_shapes = _get_hierarchy_shapes(rows, style)

            # Divide different node kinds by special lines.
            kind_shapes = _get_kind_shapes(rows, style)

        highlight_shapes = _get_highlight_shapes(rows, cols, style)

        # Combine all traces and shapes.
        traces = pie_traces
        shapes = highlight_shapes + grid_shapes + pie_shapes + kind_shapes + hierarchy_shapes

        dim = (len(rows), len(cols))
        xaxis, yaxis = deepcopy(style.piemap.xaxis), deepcopy(style.piemap.yaxis)
        xaxis.update(range=[0, dim[1]], scaleanchor="y", scaleratio=1.0)
        yaxis.update(range=[0, dim[0]])

        super().__init__(
            width=dim[1] * style.boxsize,
            height=dim[0] * style.boxsize,
            traces=traces,
            shapes=shapes,
            xaxis=xaxis,
            yaxis=yaxis,
        )


def _get_grid_shapes(rows: List[Node], cols: List[Node], style: Style):
    """Get grid traces and shapes for the mapping plot component.

    Arguments:
        rows: The nodes to be placed on the rows of the matrix.
        cols: The columns to be placed on the columns of the matrix.
        style: Plot style mapping.
    """
    dim = (len(rows), len(cols))

    line = style.piemap.gridline
    xstep, ystep = style.xstep, style.ystep

    # Gridlines
    shapes = [
        svg.get_line(x0=0, x1=dim[1] * xstep, y0=i * ystep, y1=i * ystep, line=line).as_dict()
        for i in range(dim[0] + 1)
    ] + [
        svg.get_line(x0=j * xstep, x1=j * xstep, y0=0, y1=dim[0] * ystep, line=line).as_dict()
        for j in range(dim[1] + 1)
    ]

    if rows == cols:
        shapes += [
            svg.get_rectangle(
                x0=i,
                x1=i + 1,
                y0=dim[0] - 1 - i,
                y1=dim[0] - i,
                fillcolor=line.color,
                line=dict(color=line.color),
                layer="below",
            ).as_dict()
            for i in range(dim[1])
        ]

    return shapes


def _get_highlight_shapes(rows: List[Node], cols: List[Node], style: Style) -> List[Dict[str, Any]]:
    """Get highlight bands for both rows and columns."""
    row_annot = (
        style.piemap.highlight_row_annotation
        if style.piemap.highlight_row_annotation
        else style.highlight_annotation
    )
    col_annot = (
        style.piemap.highlight_col_annotation
        if style.piemap.highlight_col_annotation
        else style.highlight_annotation
    )
    dim = (len(rows), len(cols))
    xstep, ystep = style.xstep, style.ystep

    shapes = []

    if col_annot:
        for i, node in enumerate(cols):
            value = node.annotations.get(col_annot)
            if not value:
                continue
            if isinstance(value, str):
                color = value
            else:
                color = (
                    style.piemap.highlight_col_color
                    if style.piemap.highlight_col_color
                    else style.highlight_color
                )
            shapes.append(
                svg.get_rectangle(
                    i * xstep,
                    (i + 1) * xstep,
                    0,
                    dim[0] * ystep,
                    fillcolor=color,
                    line=svg.Line(width=0),
                    layer="below",
                ).as_dict()
            )

    if row_annot:
        for i, node in enumerate(rows):
            value = node.annotations.get(row_annot)
            if not value:
                continue
            if isinstance(value, str):
                color = value
            else:
                color = (
                    style.piemap.highlight_row_color
                    if style.piemap.highlight_row_color
                    else style.highlight_color
                )
            shapes.append(
                svg.get_rectangle(
                    0,
                    dim[1] * xstep,
                    (dim[0] - 1 - i) * ystep,
                    (dim[0] - i) * ystep,
                    fillcolor=color,
                    line=svg.Line(width=0),
                    layer="below",
                ).as_dict()
            )

    return shapes


def _get_pies_data(rows: List[Node], cols: List[Node], edges: List[Edge], style: Style):
    """Get piechart traces and shapes for the mapping plot component.

    Arguments:
        rows: List of row nodes.
        cols: List of col nodes.
        edges: List of edges to draw data from.
        style: Plot style mapping.
    """
    # Dimensions
    dim = (len(rows), len(cols))

    # Get fields from style object or select all for the set display setting.
    fields = _get_fields(edges, style)

    # Check if categorical color settings are correct.
    _check_categorical_color_settings(fields=fields, style=style)

    # Prepare equal wedge angles once if that's the mode.
    equal_angles = _get_equal_angles(fields) if style.piemap.mode == "equal" else None

    # Get edge bundles.
    bundle_dict = _get_bundle_dict(rows, cols, edges, style)

    # Get fields dict.
    fields_dict, field_lower, field_upper = _get_fields_dict(bundle_dict, fields, style)

    # Calculate actual traces and shapes.
    traces = []
    shapes = []
    for i, col in enumerate(cols):
        if style.convention == Convention.IR_FAD:
            source = col
        elif style.convention == Convention.IC_FBD:
            target = col
        else:
            raise ValueError("Unknown matrix convention.")

        for j, row in enumerate(rows):
            if style.convention == Convention.IR_FAD:
                target = row
            elif style.convention == Convention.IC_FBD:
                source = row
            else:
                raise ValueError("Unknown matrix convention.")

            bundle = bundle_dict[source.name, target.name]
            if not bundle:
                continue  # No edges here.
            field_values = fields_dict[source.name, target.name]

            # Equal angles if calculated else calculate relative ones.
            field_angles = (
                _get_relative_angles(fields, field_values) if equal_angles is None else equal_angles
            )

            # Get the scaled radius.
            radius = (
                style.piemap.radius
                if style.piemap.scale_weight is None
                else style.piemap.radius
                * prod(e.weights.get(style.piemap.scale_weight, 1.0) for e in bundle)
            )

            # Draw the pie chart.
            customdata = _get_customdata(bundle, style)
            customdata.update(dict(source=source.name, target=target.name))
            pie_traces, pie_shapes = _get_pie_data(
                fields,
                field_angles,
                field_values,
                field_lower,
                field_upper,
                style,
                customdata=customdata,
                x=i + 0.5,
                y=dim[0] - j - 0.5,
                r=radius,
            )
            traces.extend(pie_traces)
            shapes.extend(pie_shapes)

    return traces, shapes


def _get_bundle_dict(
    rows: List[Node], cols: List[Node], edges: List[Edge], style: Style
) -> Dict[Tuple[str, str], List[Edge]]:
    """Get (inherited) edge lists between sources (cols) and targets (rows)."""
    # Basic edge mapping.
    edge_dict: Dict[Tuple[str, str], List[Edge]] = defaultdict(list)
    for e in edges:
        edge_dict[e.source.name, e.target.name].append(e)

    # Without inheritance, this edge dict is just the result we want.
    if not style.piemap.inherit:
        return edge_dict

    # Calculate edge bundles:
    bundle_dict: Dict[Tuple[str, str], List[Edge]] = defaultdict(list)
    for col in cols:
        if style.convention == Convention.IR_FAD:
            source = col
        elif style.convention == Convention.IC_FBD:
            target = col
        else:
            raise ValueError("Unknown matrix convention.")

        for row in rows:
            if style.convention == Convention.IR_FAD:
                target = row
            elif style.convention == Convention.IC_FBD:
                source = row
            else:
                raise ValueError("Unknown matrix convention.")

            bundle = edge_dict[source.name, target.name]
            bundle.extend(
                e
                for s in source.descendant_gen
                for t in target.descendant_gen
                for e in edge_dict[s.name, t.name]
            )
            bundle_dict[source.name, target.name] = bundle

    return bundle_dict


def _get_fields_dict(
    bundle_dict: Dict[Tuple[str, str], List[Edge]], fields: List[str], style: Style
) -> Tuple[Dict[Tuple[str, str], Dict[str, float]], Dict[str, float], Dict[str, float]]:
    """Get field values (display values) for each source/target combination."""
    # Get all field values.
    # Calculate once re-use later.
    fields_dict: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(dict)
    field_lower: Dict[str, float] = dict()
    field_upper: Dict[str, float] = dict()
    for (src, tgt), bundle in bundle_dict.items():
        # Get values for the selected fields in this display mode.
        field_values = _get_field_values(bundle, fields, style)
        fields_dict[src, tgt] = field_values

        # Update lower/upper bounds.
        for field, val in field_values.items():
            if field not in field_lower or val < field_lower[field]:
                field_lower[field] = val
            if field not in field_upper or val > field_upper[field]:
                field_upper[field] = val
    return fields_dict, field_lower, field_upper


def _get_customdata(edges: List[Edge], style: Style) -> Dict[str, Any]:
    """Get customdata from edges."""
    customdata = {}

    for key in style.piemap.customhoverkeys:
        data = []
        for e in edges:
            if not hasattr(e.annotations, key):
                continue
            data.append(str(e.annotations[key]))

        customdata[key] = "<br>".join(data)

    return customdata


def _get_fields(edges: List[Edge], style: Style) -> List[str]:
    """Get fields from style mapping or default to all available fields to display."""
    style_fields = style.piemap.fields
    if style_fields is not None:
        return style_fields

    display = style.piemap.display
    if display == "kinds":
        fields = set(e.kind for e in edges)
    elif display == "labels":
        fields = set(label for e in edges for label in e.labels)
    elif display in {"weight labels", "weights"}:
        fields = set(wl for e in edges for wl in e.weights.keys())
    else:
        fields = set()

    return sorted(fields)


def _check_categorical_color_settings(fields: List[str], style: Style):
    """Check if categorical colors list is of sufficient length (len=10 by default)."""
    if style.piemap.display == "weights":
        return

    if len(fields) > len(style.palettes.categorical):
        style.palettes.categorical = colors.get_categorical(len(fields))


def _get_field_values(edges: List[Edge], fields: List[str], style: Style) -> Dict[str, float]:
    """Get the field sums for the given edges according to the style."""
    field_map: Dict[str, float] = dict()
    if not edges:
        return field_map

    display = style.piemap.display
    if display == "kinds":
        field_map = {
            f: float(sum(f == e.kind for e in edges))
            for f in fields
            if sum(f == e.kind for e in edges)
        }
    elif display == "labels":
        field_map = {
            f: float(sum(f in e.labels for e in edges))
            for f in fields
            if sum(f in e.labels for e in edges)
        }
    elif display == "weight labels":
        field_map = {
            f: float(sum(f in e.weights for e in edges))
            for f in fields
            if sum(f in e.weights for e in edges)
        }
    elif display == "weights":
        field_map = {f: float(sum(e.weights.get(f, 0.0) for e in edges)) for f in fields}
    else:
        field_map = dict(num=float(len(edges)))
    return field_map


def _get_equal_angles(fields: List[str]) -> Dict[str, Tuple[float, float]]:
    """Get piechart angle dictionary."""
    delta = 2 * pi / len(fields) if fields else 2 * pi
    offset = pi / 2  # Start upright, then go clockwise for intuitive results.
    return {f: (offset - (i + 1) * delta, offset - i * delta) for i, f in enumerate(fields)}


def _get_relative_angles(
    fields: List[str], sums: Dict[str, float]
) -> Dict[str, Tuple[float, float]]:
    """Get the field pie-chart angles given their value sums."""
    total = sum(abs(v) for v in sums.values())
    angles = dict()
    if not total:
        return _get_equal_angles(fields)

    end = pi / 2
    for field in fields:
        if not sums.get(field):
            continue

        delta = 2 * pi * abs(sums[field]) / total
        start = end - delta
        angles[field] = (start, end)
        end = start

    return angles


def _get_pie_data(
    fields: List[str],
    angles: Dict[str, Tuple[float, float]],
    values: Dict[str, float],
    lower: Dict[str, float],
    upper: Dict[str, float],
    style: Style,
    customdata: Dict[str, Any],
    x: float = 0.0,
    y: float = 0.0,
    r: float = 0.4,
):
    """Draw pie charts in the order of the given fields."""
    display = style.piemap.display

    shapes = []
    xdata = []
    ydata = []
    textdata = []

    # Draw for every field.
    for i, field in enumerate(fields):
        if field not in angles or field not in values:
            continue

        # Get the right color.
        if display == "weights":
            color = style.palettes.get_continuous_color(
                values[field], lower[field], upper[field], field=field
            )
        else:
            color = style.palettes.get_categorical_color(i, field=field)

        # Fetch angles.
        start, end = angles[field]

        # Append shape.
        shapes.append(
            svg.get_wedge(
                x=x,
                y=y,
                r=r,
                start_angle=start,
                end_angle=end,
                fillcolor=color,
                line=dict(width=0),
            ).as_dict(),
        )

        # Calculate and append trace data.
        delta = end - start
        xdata.append(x + 0.5 * r * cos(start + 0.5 * delta))
        ydata.append(y + 0.5 * r * sin(start + 0.5 * delta))

        text = (
            f"source: {customdata['source']}"
            + f"<br>target: {customdata['target']}"
            + f"<br>{field}: {values[field]}"
        )

        for key in style.piemap.customhoverkeys:
            text += "<br>" + f"{key}: {customdata[key]}"

        textdata.append(text)

    # Get traces.
    traces = [
        go.Scatter(
            x=xdata,
            y=ydata,
            text=textdata,
            mode="markers",
            marker=dict(color="#ffffff"),
            hoverinfo="text",
            showlegend=False,
            customdata=[customdata],
        )
    ]

    return traces, shapes


def _get_hierarchy_shapes(leafs: List[Node], style: Style) -> List[Dict[str, Any]]:
    """Get hierarchy shapes for the mapping plot component.

    Arguments:
      leafs: List of leaf nodes.
      style: Style of the tree to be plotted.

    Returns:
        Hierarchy shapes as SVG mappings converted to dictionaries.
    """

    shapes: List[Dict[str, Any]] = []

    # Plot geometrics
    x_step, y_step = style.xstep, style.ystep
    tree_depth = max([node.depth for node in leafs], default=0)
    dim = len(leafs)

    # Compute leaf node positions.
    odict = OrderedDict()
    sdict = OrderedDict()
    for i, n in enumerate(leafs):
        odict[n] = i  # Offset dict
        sdict[n] = 1  # Size dict

    # Compute ancestor positions.
    processed_ancestors = set()
    parents = set(node.parent for node in leafs if node.parent)
    current_depth = tree_depth - 1
    while parents:
        grandparents = set()
        for parent in parents:
            if parent in processed_ancestors:
                continue
            if parent.depth < current_depth:
                grandparents.add(parent)
                continue

            # Only take into account children that are visible.
            children = [child for child in parent.children if child in odict]

            # Offset is minimum value.
            offset = min(odict[n] for n in children) if children else 0
            odict[parent] = offset

            # Size is sum of child sizes.
            size = sum(sdict[n] for n in children)
            sdict[parent] = size

            shapes.append(
                svg.get_rectangle(
                    x0=offset * x_step,
                    x1=(offset + size) * x_step,
                    y0=(dim - offset - size) * y_step,
                    y1=(dim - offset) * y_step,
                    line=style.piemap.clusterline,
                ).as_dict()
            )

            processed_ancestors.add(parent)
            if parent.parent:
                grandparents.add(parent.parent)

        parents = grandparents
        current_depth -= 1

    busarea = style.piemap.busarea

    for node in sdict:
        if node.is_bus and node.parent in sdict:
            assert node.parent is not None
            parent_size = sdict[node.parent]
            parent_offset = odict[node.parent]
            node_offset = odict[node]
            node_size = sdict[node]

            # Horizontal bus bar.
            shapes.append(
                svg.get_rectangle(
                    x0=parent_offset * x_step,
                    x1=(parent_offset + parent_size) * x_step,
                    y0=(dim - node_offset - node_size) * y_step,
                    y1=(dim - node_offset) * y_step,
                    **busarea.as_dict(),
                ).as_dict()
            )

            # Vertical bus bar.
            shapes.append(
                svg.get_rectangle(
                    x0=node_offset * x_step,
                    x1=(node_offset + node_size) * x_step,
                    y0=(dim - parent_offset - parent_size) * y_step,
                    y1=(dim - parent_offset) * y_step,
                    **busarea.as_dict(),
                ).as_dict()
            )

    return shapes


def _get_kind_shapes(leafs: List[Node], style: Style) -> List[svg.SVG]:
    """Get kind shapes for the mapping plot component."""
    shapes = []
    if not leafs:
        return shapes
    dim = len(leafs)
    line = style.piemap.kindline

    # Get the indexes of leafs that "change" the kind and append lines afterwards.
    kind = leafs[0].kind
    for i, node in enumerate(leafs):
        if node.kind == kind:
            continue
        kind = node.kind

        # Calculate y coordinate of horizontal line.
        y = (dim - i) * style.ystep

        # Horizontal line.
        shapes.append(svg.get_line(x0=0, x1=dim, y0=y, y1=y, line=line).as_dict())

        # Vertical line.
        shapes.append(svg.get_line(x0=i, x1=i, y0=0, y1=dim, line=line).as_dict())

    return shapes
