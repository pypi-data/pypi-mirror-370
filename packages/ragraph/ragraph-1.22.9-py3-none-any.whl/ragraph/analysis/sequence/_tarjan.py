"""Tarjan's Depth First Search Algorithm."""

from typing import Dict, List, Optional, Tuple, Union

from ragraph.analysis._classes import SequenceAnalysis
from ragraph.graph import Graph
from ragraph.node import Node

tarjans_dfs_analysis = SequenceAnalysis(
    "Tarjan's Depth First Search Algorithm",
    description="""\
    Sort an directed acyclic graph (DAG) in it's sequential order.

    Note:
        Can only parse nodes which form a directed acyclic graph (DAG).
    """,
)


@tarjans_dfs_analysis
def tarjans_dfs(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[str], List[Node]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, List[Node]]:
    """docstring stub"""
    assert nodes
    out = []
    unmarked = [n for n in nodes if isinstance(n, Node)]
    state = {n: "todo" for n in nodes}

    targets_of: Dict[Node, List[Node]] = {
        source: [
            target
            for target in unmarked
            if any(graph.edges_between(source, target, inherit=inherit, loops=False))
        ]
        for source in unmarked
    }

    def visit(n: Node):
        s = state[n]
        if s == "done":
            return
        if s == "temp":
            raise ValueError("Not a Directed Acyclic Graph (DAG).")
        state[n] = "temp"
        for m in targets_of[n]:
            visit(m)
        state[n] = "done"
        out.append(n)

    while unmarked:
        node = unmarked.pop()
        if state[node] == "done":
            continue
        visit(node)

    return graph, out[::-1]
