"""
# Tarjan's strongly connected components algorithm.

Reference:
    Tarjan, R. (1972). Depth-First Search and Linear Graph Algorithms.
    SIAM Journal on Computing, 1(2), 146-160.
    [DOI: 10.1137/0201010] (https://doi.org/10.1137/0201010)
"""

from textwrap import dedent
from typing import Dict, List, Optional, Tuple, Union

from ragraph.analysis._classes import ClusterAnalysis
from ragraph.analysis._utils import create_parent
from ragraph.graph import Graph
from ragraph.node import Node

tarjans_scc_analysis = ClusterAnalysis(
    "Tarjan's strongly connected components clustering algorithm.",
    description=dedent(
        """Clusters all strongly connected components (cycles) in a graph.
        Ignores the `loops` and `edge_weights` parameters."""
    ),
)


@tarjans_scc_analysis
def tarjans_scc(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, Union[List[Node], List[str]]]:
    """docstring stub"""
    assert leafs is not None
    clusters = tarjans_scc_algorithm(graph, leafs, inherit)  # type: ignore

    cluster_roots = []
    for children in clusters:
        if len(children) > 1:
            parent = create_parent(graph, children)
            cluster_roots.append(parent)
        else:
            cluster_roots.append(children[0])

    return graph, cluster_roots


def tarjans_scc_algorithm(graph: Graph, nodes: List[Node], inherit: bool) -> List[List[Node]]:
    """Tarjan's strongly connected components algorithm.

    Arguments:
        graph: Graph to detect SCC's in (cycles).
        nodes: List of nodes (components) to detect SCC's for.
        inherit: Whether to take into account (inherit) edges between children during
            calculations.

    Returns:
        Lists of strongly connected components.

    Reference:
        Tarjan, R. (1972). Depth-First Search and Linear Graph Algorithms.
            SIAM Journal on Computing, 1(2), 146-160. https://doi.org/10.1137/0201010
    """
    out = []
    index = 0
    indexes: Dict[Node, int] = {n: -1 for n in nodes}
    lowlinks: Dict[Node, int] = {n: -1 for n in nodes}
    onstacks: Dict[Node, int] = {n: -1 for n in nodes}
    stack = []

    targets_of: Dict[Node, List[Node]] = {
        source: [
            target
            for target in nodes
            if any(graph.edges_between(source, target, inherit=inherit, loops=False))
        ]
        for source in nodes
    }

    def strongconnect(n: Node):
        nonlocal index
        indexes[n] = index
        lowlinks[n] = index
        index = index + 1
        stack.append(n)
        onstacks[n] = True

        for m in targets_of[n]:
            if indexes[m] == -1:
                strongconnect(m)
                lowlinks[n] = min(lowlinks[n], lowlinks[m])  # type: ignore
            elif onstacks[m]:
                lowlinks[n] = min(lowlinks[n], indexes[m])  # type: ignore

        if lowlinks[n] == indexes[n]:
            scc = []
            k = None
            while n != k:
                k = stack.pop()
                onstacks[k] = False
                scc.append(k)
            out.append(scc)

    for node in nodes:
        if indexes[node] == -1:
            strongconnect(node)

    return out
