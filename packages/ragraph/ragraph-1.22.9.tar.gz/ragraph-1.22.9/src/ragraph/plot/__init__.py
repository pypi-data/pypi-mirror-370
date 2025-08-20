"""# RaGraph plotting module"""

from typing import Any, Dict, Iterable, List, Optional

from plotly import graph_objects as go

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.plot.generic import Style

__all__ = ["Style", "dsm", "dmm", "mdm"]

try:
    from ragraph.plot.components.chord import chord  # noqa

    __all__.append("chord")
except ModuleNotFoundError:
    pass


def __getattr__(name: str) -> Any:
    """Lazily import optional modules."""
    if name == "chord":
        from ragraph.plot.components.chord import chord

        return chord
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def dsm(
    leafs: List[Node],
    edges: List[Edge],
    style: Style = Style(),
    sort: bool = True,
    sort_args: Dict[str, Any] = dict(),
    node_kind: Optional[str] = None,
    show: bool = False,
) -> go.Figure:
    """Get a DSM plot of a Graph object.

    Arguments
        leafs: The nodes to be placed on the rows and columns of the matrix..
        edges: Edges to be displayed between leaf nodes.
        style: Plot style option mapping.
        sort: Boolean to indicate whether the rows and cols should be sorted following
            the hierarchical structure.
        node_kind: The node kind to be displayed.
        show: Boolean to display the figure.
    """
    node_kinds = [node_kind] if node_kind else list({n.kind for n in leafs})
    assert (
        len(node_kinds) == 1
    ), "A DSM should only contain one node kind. See MDM for multi-domain matrices."

    return mdm(
        leafs,
        edges,
        style=style,
        sort=sort,
        sort_args=sort_args,
        node_kinds=node_kinds,
        show=show,
    )


def dmm(
    rows: List[Node],
    cols: List[Node],
    edges: List[Edge],
    style: Style = Style(),
    sort: bool = True,
    row_node_kinds: Optional[List[str]] = None,
    row_sort_args: Dict[str, Any] = dict(),
    col_node_kinds: Optional[List[str]] = None,
    col_sort_args: Dict[str, Any] = dict(),
    show: bool = False,
) -> go.Figure:
    """Get a domain-mapping-matrix (DMM) plot of a Graph object.

    Arguments:
        rows: The nodes to be placed on the rows of the matrix.
        cols: The columns to be placed on the columns of the matrix.
        edges: Edges to be displayed between leaf nodes.
        style: Plot style option mapping.
        sort: Boolean to indicate whether the rows and cols should be sorted following
            the hierarchical structure.
        row_node_kinds: The node kinds displayed on the rows.
        col_node_kinds: The node kinds displayed on the columns.
        show: Boolean to display the figure.

    Returns:
       Domain-mapping matrix figure.
    """
    from ragraph.plot import utils

    if sort:
        rows = utils.get_axis_sequence(rows, kinds=row_node_kinds, **row_sort_args)
        cols = utils.get_axis_sequence(cols, kinds=col_node_kinds, **col_sort_args)

    grid = utils.get_dmm_grid(rows=rows, cols=cols, edges=edges, style=style)

    fig = utils.get_subplots(grid, style=style)
    return utils.process_fig(fig=fig, show=show, style=style)


def mdm(
    leafs: List[Node],
    edges: List[Edge],
    style: Style = Style(),
    sort: bool = True,
    sort_args: Dict[str, Any] = dict(),
    node_kinds: Optional[List[str]] = None,
    show: bool = False,
) -> go.Figure:
    """Get a Multi-Domain Matrix (MDM) plot of a Graph object.

    Arguments
        leafs: The nodes to be placed on the rows and columns of the matrix..
        edges: Edges to be displayed between leaf nodes.
        style: Plot style option mapping.
        sort: Boolean to indicate whether the rows and cols should be sorted following
            the hierarchical structure.
        node_kinds: The node kinds displayed within the matrix.
        show: Boolean to display the figure.
    """
    from ragraph.plot import utils

    if sort:
        leafs = utils.get_axis_sequence(leafs, kinds=node_kinds, **sort_args)

    grid = utils.get_mdm_grid(leafs=leafs, edges=edges, style=style)

    fig = utils.get_subplots(grid, style=style)

    return utils.process_fig(fig=fig, show=show, style=style)


def delta_dsm(g1: Graph, g2: Graph, *args, style: Style = Style(), **kwargs) -> go.Figure:
    """Get a delta-DSM plot between two Graph objects."""
    raise NotImplementedError()


def sigma_dsm(graphs: Iterable[Graph], *args, style: Style = Style(), **kwargs) -> go.Figure:
    """Get a sigma-DSM plot of any number of Graph objects."""
    raise NotImplementedError()


def network(g: Graph, *args, style: Style = Style(), **kwargs) -> go.Figure:
    """Get a network plot of a Graph object."""
    raise NotImplementedError()
