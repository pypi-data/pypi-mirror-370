"""
# Gamma bus detection

References:
    Wilschut, T., Etman, L. F. P., Rooda, J. E., & Adan, I. J. B. F. (2017). Multilevel
    Flow-Based Markov Clustering for Design Structure Matrices. Journal of Mechanical
    Design, 139(12), 121402. [DOI: 10.1115/1.4037626](https://doi.org/10.1115/1.4037626)
"""

from typing import List, Optional, Tuple, Union

import numpy as np

from ragraph.analysis._classes import Bound, BusAnalysis, Parameter
from ragraph.graph import Graph, Node

gamma_params = {
    p.name: p
    for p in [
        Parameter(
            "gamma",
            float,
            "Threshold factor for bus nodes with respect to the median of the "
            "(nonzero) node degree distribution.",
            default=2.0,
            lower=Bound(1.0, inclusive=True, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        )
    ]
}

gamma_analysis = BusAnalysis(
    name="Gamma bus detection",
    description="Detect bus nodes by selecting node degree outliers by some factor "
    + "gamma w.r.t. median of nonzero node degrees.",
    parameters=gamma_params,
)


@gamma_analysis
def gamma_bus_detection(
    graph: Graph,
    root: Optional[Union[Node, str]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    names: bool = False,
    gamma: float = gamma_params["gamma"].default,  # type: ignore
    safe: bool = True,
    **kwargs,
) -> Union[Tuple[List[Node], List[Node]], Tuple[List[str], List[str]]]:
    """Detect bus nodes in a graph.

    Arguments:
        graph: Graph to detect bus nodes in.
        root: Root node of this bus detection analysis.
        leafs: Optional list of nodes to consider leafs during this bus detection cycle.
        inherit: Whether edges between descendants of nodes should be taken into account
            (if applicable).
        loops: Whether self-loop edges should be taken into account (if applicable).
        gamma: Bus threshold w.r.t. median of nonzero node degrees.
        names: Whether to return node names or node instances.

    Returns:
        Bus leafs.
        Nonbus leafs.

    Note:
        Works by selecting node degree outliers by some factor gamma w.r.t. median of
        nonzero node degrees.

    Reference:
        Wilschut, T., Etman, L. F. P., Rooda, J. E., & Adan, I. J. B. F. (2017). Multilevel
        Flow-Based Markov Clustering for Design Structure Matrices. Journal of Mechanical
        Design, 139(12), 121402. https://doi.org/10.1115/1.4037626
    """
    matrix = graph.get_adjacency_matrix(
        nodes=leafs, inherit=inherit, loops=loops, only=edge_weights
    )
    assert isinstance(matrix, np.ndarray)
    assert leafs is not None
    dim = matrix.shape[0]

    # Calculate interface matrix and node degrees.
    interfaces = matrix > 0
    degrees = interfaces.sum(0) + interfaces.sum(1)

    # Initialize arrays and enter heuristic.
    nonbus_idxs: np.ndarray = np.arange(dim)
    bus_idxs: np.ndarray = np.int_([])
    while nonbus_idxs.size > 1:
        nonbus_nonzero_degrees = degrees[nonbus_idxs][degrees[nonbus_idxs] > 0]

        # Calculate threshold if nonzero degree nonbus nodes are left.
        if not nonbus_nonzero_degrees.size:
            break
        threshold = gamma * np.median(nonbus_nonzero_degrees)

        # Transfer nodes to bus if found.
        add_bus = nonbus_idxs[degrees[nonbus_idxs] >= threshold]
        if not add_bus.size:
            break
        setdiff = np.setdiff1d(nonbus_idxs, add_bus, assume_unique=True)
        bus_idxs = np.hstack((bus_idxs, add_bus))
        nonbus_idxs = setdiff

    # If all nodes were assigned to the bus, actually none are.
    if len(bus_idxs) != dim and len(bus_idxs) > 0:
        bus_leafs = [leafs[i] for i in bus_idxs]
        nonbus_leafs = [leafs[i] for i in nonbus_idxs]
    else:
        bus_leafs = []
        nonbus_leafs = leafs

    return bus_leafs, nonbus_leafs
