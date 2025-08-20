"""# Chord plots usings openchord"""

from typing import Any, Dict, List, Optional, Union

from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.plot.generic import Style

try:
    import rachord
except ImportError:
    raise ModuleNotFoundError(
        "Could not find the `rachord` dependency. To use the chord plot functionality, "
        "RaGraph needs to be installed as `ragraph[plot]` or `ragraph[all]`."
    )


def chord(
    graph: Graph,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    style: Optional[Style] = None,
    adj_kwargs: Optional[Dict[str, Any]] = None,
    symmetrize: bool = False,
    show: bool = False,
) -> rachord.Chord:
    """Make a chord plot for the given nodes in a graph.

    Arguments:
        graph: Graph to create a chord plot for.
        nodes: Nodes or node names to include in the chord plot. Defaults to leaf nodes.
        style: Plotting style.
        adj_kwargs: Additional arguments to [`ragraph.graph.Graph.get_adjacency_matrix`
            ][ragraph.graph.Graph.get_adjacency_matrix].
        symmetrize: Whether to symmetrize the adjacency matrix.
        show: Whether to show the resulting figure.

    Returns:
        Chord plot using rachord.
    """
    nodes = graph.leafs if nodes is None else nodes
    nodes = [n if isinstance(n, Node) else graph.node_dict[n] for n in nodes]
    labels = [n.name for n in nodes]

    adj_kwargs = dict() if adj_kwargs is None else adj_kwargs
    adj = graph.get_adjacency_matrix(nodes=nodes, **adj_kwargs)

    if symmetrize:
        dim = len(nodes)
        for row in range(dim):
            for col in range(row, dim):
                value = (adj[row][col] + adj[col][row]) / 2
                adj[row][col] = value
                adj[col][row] = value

    style: Style = Style() if style is None else style
    cs = style.chord
    fig = rachord.Chord(adj, labels, radius=cs.radius)
    fig.padding = (
        cs.fontsize * cs.fontfactor * max(len(x) for x in labels)
        if cs.padding is None
        else cs.padding
    )
    fig.gap_size = cs.gap_size
    fig.ribbon_gap = cs.ribbon_gap
    fig.ribbon_stiffness = cs.ribbon_stiffness
    fig.arc_thickness = cs.arc_thickness
    fig.bg_color = cs.bg_color
    fig.bg_transparency = cs.bg_transparency
    fig.font_size = cs.fontsize
    fig.font_family = cs.fontfamily

    fig.colormap = style.palettes.categorical

    if show:
        return fig.show()
    else:
        return fig
