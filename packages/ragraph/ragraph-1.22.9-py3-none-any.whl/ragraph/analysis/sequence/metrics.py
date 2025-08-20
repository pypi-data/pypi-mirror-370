"""Sequence metrics."""

from typing import List, Optional, Tuple, Union

import numpy as np

from ragraph.graph import Graph
from ragraph.node import Node


def feedback_marks(mat: np.ndarray) -> Tuple[float, np.ndarray]:
    """Measure the sum of feedback marks in an adjacency matrix.

    Arguments:
        mat: Adjacency matrix to analyze.

    Returns:
        Resulting metric.
        Cell contribution matrix.

    References:
        Steward, D. V., 1981, Systems Analysis and Management: Structure, Strategy and
            Design, Petrocelli Books, New York.
        Kusiak, A., & Wang, J. (1993). Decomposition of the Design Process. Journal of
            Mechanical Design, 115(4), 687. https://doi.org/10.1115/1.2919255
    """
    contrib = np.triu(mat, 1)
    return contrib.sum(), contrib


def feedback_distance(mat: np.ndarray) -> Tuple[float, np.ndarray]:
    """Measure the feedback length, e.g. distance from the adjacency matrix diagonal.

    Arguments:
        mat: Adjacency matrix to analyze.

    Returns:
        Resulting metric.
        Cell contribution matrix.

    References:
        Gebala, D. A., & Eppinger, S. D. (1991). Methods for analyzing design
            procedures. ASME Design Technical Conferences (Design Theory and
            Methodology), 227-233. Miami.
    """
    dim = len(mat)

    dimtile = np.tile(np.arange(dim), (dim, 1))
    ddist = dimtile - dimtile.T

    contrib = np.triu(mat, 1) * ddist
    return contrib.sum(), contrib


def lower_left(mat: np.ndarray) -> Tuple[float, np.ndarray]:
    """Measure the distance to the lower left of the adjacency matrix.

    Arguments:
        mat: Adjacency matrix to analyze.

    Returns:
        Resulting metric.
        Cell contribution matrix.

    References:
        Todd, D. S. (1997). Multiple criteria genetic algorithms in engineering design
            and operation. University of Newcastle.
    """
    dim = len(mat)

    dimtile = np.tile(np.arange(dim), (dim, 1))
    lldist = dimtile - dimtile.T + dim - 1

    contrib = mat * lldist
    return contrib.sum(), contrib


def feedback_lower_left(
    mat: np.ndarray, fb: float = 100.0, ff: float = 1.0
) -> Tuple[float, np.ndarray]:
    """Jointly measure lower left distance to the adjacency matrix diagonal and
    feedback marks. Feedback and feedforward are penalized differently, but both via a
    quadratic lower-left distance factor.

    Arguments:
        mat: Adjacency matrix to analyze.
        fb: Feedback adjacency multiplier.
        ff: Feedforward adjacency multiplier.

    Returns:
        Resulting metric.
        Cell contribution matrix.

    Note:
        Feedback marks above the diagonal are weighted 100 times more than those below
        the diagonal. The multiplier is offset by (n-1)^2.

    References:
        Scott, J. A. (1999). A strategy for modelling the design-development phase of a
            product. University of Newcastle. See Equation 6.1 and Figure 6.4.
    """
    dim = len(mat)

    dimtile = np.tile(np.arange(1, dim + 1), (dim, 1))
    lldist = dimtile - dimtile.T + dim
    omega = np.square(lldist)

    # Lower triangle
    omgl = ff * omega
    tril = np.tril(mat, -1)
    resl = omgl * tril

    # Upper triangle
    omgu = fb * omega
    triu = np.triu(mat, 1)
    resu = omgu * triu

    contrib = resl + resu
    return contrib.sum(), contrib


def feedback_crossover(
    mat: np.ndarray, fb: float = 0.9, co: float = 0.1
) -> Tuple[float, Tuple[np.ndarray, np.ndarray]]:
    """Jointly measure feedback marks and crossovers in an adjacency matrix.

    Arguments:
        mat: Adjacency matrix to analyze.
        fb: Weight of feedback marks.
        co: Weight of feedback crossovers.

    Returns:
        Resulting metric.
        Cell contribution matrices (feedback, crossover).

    Note:
        Crossovers are where the "axis" from feedback marks towards the diagonal cross,
        except when this crossing is a feedback mark in itself. Multiple lines from
        "above" in the matrix are summed, those from the right are **NOT** (treated as
        binary).

    References:
        McCulley, C., and Bloebaum, C. L., 1996, “A Genetic Tool for Optimal Design
            Sequencing in Complex Engineering Systems,” Struct. Optim., 12(2), pp.
            186-201.
    """
    # Treat binary matrix
    mat = (mat > 0) * 1.0

    # contrib_fb is upper triangularized
    total_fb, contrib_fb = feedback_marks(mat)

    # vertical cum sum (number of accumulated marks from the top until diagonal)
    vcumsum = np.triu(np.cumsum(contrib_fb, axis=0), 1)

    # horizontal "line" multiplier, 1s toward the left from the rightmost 1 except the
    # marks themselves:
    # rows of [0,0,1,0,0,1,0,0,0]
    # become  [1,1,0,1,1,0,0,0,0]
    hline = np.cumsum(contrib_fb[:, ::-1], axis=1)[:, ::-1]
    hline = (hline > 0) * 1.0 - contrib_fb
    # no need to np.triu() here, since vcumsum already is upper triangularized.

    # Contribution matrix at crossover points and total score.
    contrib_co = vcumsum * hline
    total_co = contrib_co.sum()

    return fb * total_fb + co * total_co, (contrib_fb, contrib_co)


def net_markov_flow_adjacency(
    mat: np.ndarray,
    inf: float = 1.0,
    dep: float = 1.0,
    mu: float = 2.0,
    scale: bool = True,
) -> np.ndarray:
    """Calculate a flow balance as if the matrix would constitute a (weighted)
    Markov chain.

    Arguments:
        mat: Adjacency matrix to analyze.
        inf: The weight to subtract outgoing flow by.
        dep: The weight to add incoming flow by.
        mu: Evaporation constant when calculating flow through nodes.
        scale: Whether to scale the inflow vector according to the adjacency matrix
            column sums.

    Returns:
        Nodal flow balance as an array.
    """
    from ragraph.analysis.cluster._markov import MarkovFlow

    flow = MarkovFlow(mat, mu, scale).flow_matrix[:-1, :-1]  # Exclude sink.
    inf_vector = flow.sum(axis=0)
    dep_vector = flow.sum(axis=1)
    return dep * dep_vector - inf * inf_vector


def net_markov_flow_graph(
    graph: Graph,
    nodes: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    inf: float = 1.0,
    dep: float = 1.0,
    mu: float = 2.0,
) -> np.ndarray:
    """Calculate a flow balance as if the graph would constitute a (weighted)
    Markov chain.

    Arguments:
        graph: Graph to analyze nodes of.
        nodes: Set of node (names) to calculate the flow with.
        inherit: Whether to take into account edges between descendants of nodes.
        loops: Whether to take into account self-loop edges.
        inf: The weight to subtract outgoing flow by.
        dep: The weight to add incoming flow by.
        mu: Evaporation constant when calculating flow through nodes.

    Returns:
        Nodal flow balance as an array.

    Note:
        Uses edge inheritance to calculate an adjacency matrix.
    """
    mat = graph.get_adjacency_matrix(nodes, inherit=inherit, loops=loops)
    return net_markov_flow_adjacency(mat, inf=inf, dep=dep, mu=mu)
