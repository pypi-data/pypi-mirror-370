"""Sequence nodes by name."""

from typing import List, Optional, Tuple, Union

from ragraph.analysis._classes import SequenceAnalysis
from ragraph.graph import Graph, Node

sort_by_name_analysis = SequenceAnalysis("Sort by name")


@sort_by_name_analysis
def name(
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
    """Sequence nodes by node name.

    Arguments:
        graph: Graph to sequence nodes of.
        nodes: Nodes to sequence.

    Returns:
        Sequenced nodes.
    """
    return graph, sorted(nodes, key=lambda n: n.name)
