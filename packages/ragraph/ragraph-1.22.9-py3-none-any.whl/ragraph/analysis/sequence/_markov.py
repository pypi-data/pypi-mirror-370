"""Sorting algorithm based on the node dependency/influence in a Markov chain."""

from textwrap import dedent
from typing import List, Optional, Tuple, Union

import numpy as np

from ragraph.analysis._classes import Bound, Parameter, SequenceAnalysis
from ragraph.analysis.sequence.metrics import net_markov_flow_adjacency
from ragraph.graph import Graph, Node

markov_params = {
    p.name: p
    for p in [
        Parameter(
            "inf",
            float,
            description="Weight of relative node influence when sorting.",
            default=1.0,
            lower=Bound(0.0, inclusive=True, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "dep",
            float,
            description="Weight of relative node dependency when sorting.",
            default=1.0,
            lower=Bound(0.0, inclusive=True, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "mu",
            float,
            "Decay coefficient (usually 1.5 - 3.5). Influence or dependency of nodes "
            "decays according to this coefficient at each node it passes.",
            default=1.5,
            lower=Bound(1.0, inclusive=False, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "scale",
            bool,
            "Whether to scale in-flow with respect to adjacency column sums.",
            default=False,
        ),
    ]
}

markov_sequencing_analysis = SequenceAnalysis(
    "Markov sequencing",
    description=dedent(
        """\
    Sequencing based on relative influence and dependency as if the graph were a
    Markov chain. Internally, this converts the edge weights between nodes into a flow
    (steady state probability) distribution matrix.
    """
    ),
    parameters=markov_params,
)


@markov_sequencing_analysis
def markov(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    edge_weights: Optional[List[str]] = None,
    inf: float = markov_params["inf"].default,  # type: ignore
    dep: float = markov_params["dep"].default,  # type: ignore
    mu: float = markov_params["mu"].default,  # type: ignore
    scale: bool = markov_params["scale"].default,  # type: ignore
    inherit: bool = True,
    loops: bool = False,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, List[Node]]:
    """docstring stub"""
    assert nodes is not None
    adj = graph.get_adjacency_matrix(nodes=nodes, inherit=inherit, loops=loops, only=edge_weights)
    assert isinstance(adj, np.ndarray)

    # Obtain node penalty scores.
    penalties = net_markov_flow_adjacency(adj, inf=inf, dep=dep, mu=mu, scale=scale)

    # Calculate final sequence.
    idxs = np.argsort(penalties)

    # Reorder nodes
    seq = [nodes[i] for i in idxs]

    return graph, seq
