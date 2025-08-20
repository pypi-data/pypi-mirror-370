"""Sequencing utils."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from ragraph.analysis import logger
from ragraph.analysis._classes import BranchsortAnalysis
from ragraph.analysis.sequence.metrics import net_markov_flow_adjacency
from ragraph.graph import Graph, Node

branchsort_analysis = BranchsortAnalysis(
    "Branchsort analysis",
    description="""Sequence all branches in a hierarchy using any sequencing algorithm. Returns
    the graph, (sequenced) root nodes and sequenced leaf nodes.

    Note:
        Setting just the `root` argument will sort it's children (recursively if you want). Setting
        `nodes` is like setting multiple roots. Setting `leafs` treats the given nodes as leaf
        nodes, whose children will not be reordered.

    Note:
        It is assumed that all edges are already nicely instantiated for all their parent
        components. E.g., your root node should have it's own incoming and outgoing edges.
    """,
)


@branchsort_analysis
def branchsort(
    graph: Graph,
    algo: Callable,
    algo_args: Optional[Dict[str, Any]] = None,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    edge_weights: Optional[List[str]] = None,
    inherit: bool = True,
    loops: bool = False,
    inplace: bool = True,
    recurse: bool = True,
    names: bool = False,
    safe: bool = True,
) -> Tuple[Graph, List[Node], List[Node]]:
    """docstring stub"""
    # Sort roots
    assert isinstance(algo_args, dict)
    graph, node_sequence = algo(
        graph=graph,
        root=None,
        nodes=nodes,
        inherit=inherit,
        loops=loops,
        edge_weights=edge_weights,
        inplace=inplace,
        **algo_args,
    )
    assert node_sequence

    # Start with empty leaf sequence.
    leaf_sequence: List[Node] = []

    # Traverse branches
    for node in node_sequence:
        branchsort_analysis.log(f"Traversing '{node.name}'...")

        # Nothing to do for leaf nodes or nodes that should be treated as leafs.
        if node.is_leaf or node in leafs:  # type: ignore
            branchsort_analysis.log(f"Skipped leaf node '{node.name}'.")
            leaf_sequence.append(node)
            continue

        # Recursive case, get sorted children as the sorted "roots" of recursive call.
        if recurse:
            branchsort_analysis.log(f"Recursing into '{node.name}'...")
            _, _child_sequence, _leaf_sequence = branchsort(
                algo=algo,
                algo_args=algo_args,
                graph=graph,
                root=node,
                leafs=leafs,
                inherit=inherit,
                loops=loops,
                edge_weights=edge_weights,
                inplace=inplace,
                recurse=recurse,
            )
            leaf_sequence.extend(_leaf_sequence)
            branchsort_analysis.log(
                f"Leaf sequence extended with {[n.name for n in _leaf_sequence]}."
            )

        # Non-recursive case, get sorted children in this call.
        else:
            branchsort_analysis.log("Non-recursive call to algorithm...")
            _, _leaf_sequence = algo(
                graph=graph,
                root=node,
                inherit=inherit,
                loops=loops,
                edge_weights=edge_weights,
                inplace=inplace,
                **algo_args,
            )
            leaf_sequence.extend(_leaf_sequence)
            branchsort_analysis.log(
                f"Leaf sequence extended with {[n.name for n in _leaf_sequence]}."
            )

    return graph, node_sequence, leaf_sequence


def markov_decision(
    graph: Graph,
    options: List[Node],
    inherit: bool = True,
    loops: bool = False,
    inf: float = 1.0,
    dep: float = 1.0,
    mu: float = 1.5,
    context: Optional[List[Node]] = None,
) -> int:
    """Make a decision based on a Markov flow analysis of the adjacency matrix. The node
    with the lowest net markov flow is picked.

    Arguments:
        graph: Graph data.
        options: Nodes to decide between.
        inf: The weight to subtract outgoing flow by.
        dep: The weight to add incoming flow by.
        mu: Evaporation constant when calculating flow through nodes.
        context: Optional superset of nodes with respect to the options argument that
            constitutes the "complete" Markov chain that should be taken into account.

    Returns:
        Index of node to pick.
    """
    if context:
        adj = graph.get_adjacency_matrix(context, inherit=inherit, loops=loops)
        mapping = [context.index(option) for option in options]
        penalties = net_markov_flow_adjacency(adj, inf=inf, dep=dep, mu=mu)[mapping]
    else:
        adj = graph.get_adjacency_matrix(options, inherit=inherit, loops=loops)
        penalties = net_markov_flow_adjacency(adj, inf=inf, dep=dep, mu=mu)
    idx = np.argmin(penalties)
    logger.debug(
        f"Markov decision:\nNode {options[idx].name} has the lowest of penalties of "
        + f"{[n.name for n in options]}.\n{penalties}"
    )
    return np.argmin(penalties)
