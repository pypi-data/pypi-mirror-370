"""A sequencing algorithm for cyclic graphs that tears cycles based on a metric
(penalty) function. By default we use the metric that the Markov sequencing algorithm
uses to sort all nodes straight away.
"""

from textwrap import dedent
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

from ragraph.analysis._classes import MethodCast, Parameter, SequenceAnalysis
from ragraph.analysis.cluster._tarjan import tarjans_scc_algorithm
from ragraph.analysis.sequence.utils import markov_decision
from ragraph.graph import Graph
from ragraph.node import Node

params = {
    p.name: p
    for p in [
        Parameter(
            "inherit",
            bool,
            description="Whether to take into account (inherit) edges between "
            + "children during SCC calculations.",
            default=True,
        ),
        Parameter(
            "decision",
            Callable[
                [Graph, Union[List[Node], List[str]], Union[List[Node], List[str]]],
                int,
            ],
            description=(
                "Decision function to use. Should take a graph and a list of options ",
                "(nodes) and return an index of the selected option.",
            ),
            cast=MethodCast(),
            default=markov_decision,
        ),
        Parameter(
            "decision_args",
            Optional[Dict[str, Any]],
            description="Parameters to pass to the selected sequencing algorithm.",
            cast=lambda value: dict() if value is None else dict(value),
        ),
    ]
}


scc_tearing_analysis = SequenceAnalysis(
    "Strongly Connected Component Tearing",
    description=dedent(
        """\
    Sequencing by means of tearing Strongly Connected Components. First, the largest
    possible cycles are found and automatically sequenced using Tarjan's SCC algorithm.
    From each cycle, a node with the least penalty is then torn from the cycle and added
    to the sequence. The remainder is then again subjected to this procedure until all
    nodes have been sequenced.
    """
    ),
    parameters=params,
)


@scc_tearing_analysis
def scc_tearing(
    graph: Graph,
    decision: Callable[[Graph, List[Node]], Node],
    decision_args: Optional[Dict[str, Any]] = None,
    root: Optional[Union[str, Node]] = None,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, List[Node]]:
    """docstring stub"""
    sequence = scc_tearing_algorithm(
        graph, nodes, inherit, loops, decision, decision_args  # type: ignore
    )
    seq = list(sequence)

    return graph, seq


def scc_tearing_algorithm(
    graph: Graph,
    nodes: List[Node],
    inherit: bool,
    loops: bool,
    decision: Callable[[Graph, List[Node]], int],
    decision_args: Optional[Dict[str, Any]] = None,
) -> Generator[Node, None, None]:
    # Reverse to obtain topological order.
    sccs = tarjans_scc_algorithm(graph, nodes, inherit)[::-1]

    decision_args = dict() if decision_args is None else decision_args

    # Sequence to fill.
    for scc in sccs:
        # Sole node, add to sequence.
        if len(scc) == 1:
            sole = scc[0]
            scc_tearing_analysis.log(f"sole node '{sole.name}'")
            yield sole
            continue

        # Pick node to tear.
        tear = decision(graph, scc, **decision_args)
        torn = scc.pop(tear)
        scc_tearing_analysis.log(f"torn '{torn.name}' from {[n.name for n in scc]}.")
        yield torn
        yield from scc_tearing_algorithm(graph, scc, inherit, loops, decision, decision_args)
