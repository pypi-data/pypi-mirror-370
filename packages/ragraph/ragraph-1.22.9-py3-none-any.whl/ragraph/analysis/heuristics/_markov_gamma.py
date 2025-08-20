"""# Hierarchical Markov Clustering (HMC) with Gamma bus detection."""

from textwrap import dedent
from typing import List, Optional, Tuple, Union

from ragraph.analysis import _utils
from ragraph.analysis._classes import ClusterAnalysis, Parameter
from ragraph.analysis.bus._gamma import gamma_bus_detection, gamma_params
from ragraph.analysis.cluster._markov import (
    hierarchical_markov,
    markov_params,
)
from ragraph.graph import Graph, Node

markov_gamma_params = {
    p.name: p
    for p in [
        Parameter(
            "local_buses",
            bool,
            "Whether to detect buses locally (instead of globally).",
            default=True,
        )
    ]
}
markov_gamma_params.update(**gamma_params, **markov_params)

markov_gamma_analysis = ClusterAnalysis(
    "Hierarchical Markov clustering with Gamma bus detection",
    description=dedent(
        """\
    Cluster a given graph hierarchically with bus detection on a local level or
    globally.

    Note:
        1. A hierarchy is initialized using Hierarchical Markov Clustering.
        2. For all top-level clusters, a bus is detected.
            a. If a bus is found, both the bus and non-bus are re-clustered.
        3. Move down a level and go back to 2.
            b. If at bottom-level, stop.
    """
    ),
    parameters=markov_gamma_params,
)


@markov_gamma_analysis
def markov_gamma(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    alpha: int = markov_gamma_params["alpha"].default,  # type: ignore
    beta: float = markov_gamma_params["beta"].default,  # type: ignore
    mu: float = markov_gamma_params["mu"].default,  # type: ignore
    gamma: float = markov_gamma_params["gamma"].default,  # type: ignore
    local_buses: bool = markov_gamma_params["local_buses"].default,  # type: ignore
    max_iter: int = markov_gamma_params["max_iter"].default,  # type: ignore
    symmetrize: bool = markov_gamma_params["symmetrize"].default,  # type: ignore
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Union[List[Node], Tuple[Graph, List[Node]]]:
    """Cluster a given graph hierarchically with buses on a local level or globally."""
    assert leafs is not None
    graph, roots = hierarchical_markov(
        graph,
        root=root,
        leafs=leafs,
        inherit=inherit,
        loops=loops,
        alpha=alpha,
        beta=beta,
        mu=mu,
        edge_weights=edge_weights,
        inplace=True,
        max_iter=max_iter,
        symmetrize=symmetrize,
        names=False,
        safe=False,
    )
    check_roots = roots[:]
    checked_roots = []
    while check_roots:
        local_root = check_roots.pop()
        local_leafs = [leaf for leaf in leafs if leaf in local_root.descendants]

        # Detect bus in current root.
        bus_leafs, nonbus_leafs = gamma_bus_detection(
            graph,
            local_root,
            leafs=local_leafs,
            inherit=inherit,
            loops=loops,
            gamma=gamma,
            edge_weights=edge_weights,
            names=False,
            safe=False,
        )

        # Bus detected!
        if bus_leafs:
            # Unset local hierarchy.
            _utils.clear_local_hierarchy(graph, local_leafs, [local_root])
            local_root.children = None

            # Recalculate the nonbus hierarchy.
            graph, nonbus_roots = hierarchical_markov(
                graph,
                alpha=alpha,
                beta=beta,
                mu=mu,
                root=None,
                leafs=nonbus_leafs,
                inherit=inherit,
                loops=loops,
                edge_weights=edge_weights,
                inplace=True,
                max_iter=max_iter,
                symmetrize=symmetrize,
                names=False,
                safe=False,
            )
            _utils.set_children(graph, local_root, nonbus_roots)

            # Recalculate the bus hierarchy.
            graph, bus_roots = hierarchical_markov(
                graph,
                alpha=alpha,
                beta=beta,
                mu=mu,
                root=None,
                leafs=bus_leafs,
                inherit=inherit,
                loops=loops,
                edge_weights=edge_weights,
                inplace=True,
                max_iter=max_iter,
                symmetrize=symmetrize,
                names=False,
                safe=False,
            )
            local_root.children = bus_roots + local_root.children
            for bus in bus_roots:
                bus.is_bus = True

        # Finished this root.
        checked_roots.append(local_root)

        # If local: move down a level.
        if not check_roots and local_buses:
            check_roots = [child for local_root in checked_roots for child in local_root.children]
            checked_roots = []

    return graph, roots
