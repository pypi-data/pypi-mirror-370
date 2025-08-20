"""# Hierarchy tree plot component

This module contains the [`Tree` component][ragraph.plot.components.tree.Tree] which produces a
[`Component`][ragraph.plot.generic.Component] for the hierarchy tree of a vertical list of leaf
nodes up to their roots which are put on their left.
"""

from collections import OrderedDict
from copy import deepcopy
from typing import Any, Dict, List, Set, Tuple, Union

import plotly.graph_objs as go

from ragraph.node import Node
from ragraph.plot import svg
from ragraph.plot.generic import Component, Style


class Tree(Component):
    """Hierarchy tree plot component of leaf nodes up to their roots.

    Leaf nodes are plotted as a vertical list with their roots on the left side.

    Arguments:
        leafs: List of leaf nodes.
        style: Plot style mapping.
    """

    def __init__(self, leafs: List[Node], style: Style = Style()):
        ancestors, depth, xdict, ydict = _get_data(leafs=leafs, style=style)

        node_trace = _get_node_trace(
            xdict=xdict,
            ydict=ydict,
            style=style,
        )
        line_shapes = _get_line_shapes(ancestors=ancestors, xdict=xdict, ydict=ydict, style=style)

        # Calculating geometric boundaries.
        width = (depth + 1) * style.xstep * style.boxsize
        height = len(leafs) * style.ystep * style.boxsize

        xaxis, yaxis = deepcopy(style.tree.xaxis), deepcopy(style.tree.yaxis)
        xaxis.update(range=(-0.5, width / style.boxsize - 0.5), scaleanchor="y", scaleratio=1.0)
        yaxis.update(range=(0, height / style.boxsize))

        super().__init__(
            width=width,
            height=height,
            traces=[node_trace],
            shapes=line_shapes,
            xaxis=xaxis,
            yaxis=yaxis,
        )


def _get_data(
    leafs: List[Node], style: Style
) -> Tuple[Set[Node], int, Dict[Node, float], Dict[Node, float]]:
    """Compute coordinates of tree nodes.

    Arguments:
      leafs: List of leaf nodes.
      style: Plot style mapping.

    Returns:
        Processed ancestor nodes.
        Tree depth.
        Dictionary of node to x position of tree nodes.
        Dictionary of node to y position of tree nodes.
    """

    # Plot geometrics
    x_step = style.xstep
    y_step = style.ystep
    tree_depth = max([node.depth for node in leafs], default=0)
    tree_height = len(leafs) * y_step

    # Compute leaf node positions.
    xdict = OrderedDict()
    ydict = OrderedDict()
    for idx, leaf in enumerate(leafs):
        xdict[leaf] = tree_depth * x_step
        ydict[leaf] = tree_height - (idx + 0.5) * y_step

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

            # Calculate x positition based on parent depth.
            xdict[parent] = parent.depth * x_step

            # Calculate y position as the average of the min/max of child nodes.
            ys_children = [ydict[child] for child in parent.children if child in ydict]
            ymin = min(ys_children, default=0)
            ymax = max(ys_children, default=0)
            ydict[parent] = (ymin + ymax) / 2
            processed_ancestors.add(parent)

            if parent.parent:
                grandparents.add(parent.parent)

        parents = grandparents
        current_depth -= 1

    return processed_ancestors, tree_depth, xdict, ydict


def _get_node_trace(xdict: Dict[Node, float], ydict: Dict[Node, float], style: Style) -> go.Scatter:
    """Get tree node trace from positional dictionaries. These are the 'dots'.

    Arguments:
      xdict: Dictionary of node to x position of tree nodes.
      ydict: Dictionary of node to y position of tree nodes.
      style: Plot style mapping.

    Returns:
        Plotly Scatter trace.
    """
    xdata, ydata, textdata, customdata = (
        zip(
            *[
                (xdict[n], ydict[n], n.name, {"pointtype": "tree_node", "data": n.name})
                for n in xdict.keys()
            ]
        )
        if xdict
        else ([], [], [], [])
    )

    tree_node_trace = go.Scatter(
        x=xdata,
        y=ydata,
        text=textdata,
        mode="markers",
        marker={"color": style.tree.line.color},
        hoverinfo="text",
        showlegend=False,
        customdata=customdata,
    )

    return tree_node_trace


def _get_line_shapes(
    ancestors: Set[Node],
    xdict: Dict[Node, float],
    ydict: Dict[Node, float],
    style: Style,
) -> List[Dict[str, Any]]:
    """Compute the actual tree lines of the tree plot. These form the tree shapes.

    Arguments:
        ancestors: Set of processed ancestor nodes.
        xdict: Dictionary of node to x position of tree nodes.
        ydict: Dictionary of node to y position of tree nodes.
        style: Plot style mapping.

    Returns:
        List of SVG shapes.
    """
    svgs = []
    for node in ancestors:
        for child in node.children:
            if child not in xdict:
                continue
            svgs.extend(
                _get_parent_child_line(
                    x0=xdict[node],
                    y0=ydict[node],
                    x1=xdict[child],
                    y1=ydict[child],
                    style=style,
                )
            )
    shapes = [s.as_dict() for s in svgs]
    return shapes


def _get_parent_child_line(
    x0: Union[int, float],
    y0: Union[int, float],
    x1: Union[int, float],
    y1: Union[int, float],
    style: Style,
) -> List[svg.SVG]:
    """Draw a line with a curved 90 degree angle from a parent to a child in the tree.

    Arguments:
        x0: x starting coordinate of the line.
        y0: y starting coordinate of the line.
        x1: x ending coordinate of the line.
        y1: y ending coordinate of the line.
        style: Plot style mapping.

    Returns:
       List of SVG shape mappings of the different line sections.
    """
    linestyle = style.tree.line
    curve_delta = min(0.1, abs(y0 - y1))
    if y0 == y1:
        # Parent and child are aligned so only draw a straight line.
        return [svg.get_line(x0=x0, x1=x1, y0=y0, y1=y1, line=linestyle)]
    elif y0 > y1:
        # Draw line downwards.
        y = y1 + curve_delta
    elif y0 < y1:
        y = y1 - curve_delta

    x = x0 + curve_delta

    first_line = svg.get_line(x0=x0, x1=x0, y0=y0, y1=y, line=linestyle)
    curve_line = svg.get_curvedline(x0=x0, x1=x0, x2=x, y0=y, y1=y1, y2=y1, line=linestyle)
    second_line = svg.get_line(x0=x, x1=x1, y0=y1, y1=y1, line=linestyle)

    return [first_line, curve_line, second_line]
