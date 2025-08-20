"""
# Markov clustering module

Reference:
    Wilschut, T., Etman, L. F. P., Rooda, J. E., & Adan, I. J. B. F. (2017). Multilevel
    Flow-Based Markov Clustering for Design Structure Matrices. Journal of Mechanical
    Design, 139(12), 121402. [DOI: 10.1115/1.4037626](https://doi.org/10.1115/1.4037626)
"""

from typing import List, Optional, Tuple, Union

import numpy as np
from numpy.linalg import LinAlgError

from ragraph.analysis._classes import Bound, ClusterAnalysis, Parameter
from ragraph.analysis._utils import create_parent
from ragraph.graph import Graph, Node

markov_params = {
    p.name: p
    for p in [
        Parameter(
            "alpha",
            int,
            "Expansion coefficient. Adjacency matrix is raised to the power of alpha "
            "in each calculation cycle.",
            default=2,
            lower=Bound(1.0, inclusive=True, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "beta",
            float,
            "Inflation coefficient. Entries within the adjacency matrix are raised to "
            "the power of beta each calculation cycle.",
            default=2.0,
            lower=Bound(1.0, inclusive=False, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "mu",
            float,
            "Decay coefficient (usually 1.5 - 3.5). Influence or dependency of nodes "
            "decays according to this coefficient at each node it passes.",
            default=2.0,
            lower=Bound(1.0, inclusive=False, report="error"),
            upper=Bound(10.0, inclusive=True, report="warn"),
        ),
        Parameter(
            "max_iter",
            int,
            "Maximum number of matrix calculation cycles after which convergence is "
            "assumed instead of calculated based on machine precision.",
            default=1000,
            lower=Bound(100, inclusive=True, report="warn"),
            upper=Bound(10000, inclusive=True, report="warn"),
        ),
        Parameter(
            "symmetrize",
            bool,
            "Whether to symmetrize asymmetrical graphs.",
            default=True,
        ),
    ]
}


hierarchical_markov_analysis = ClusterAnalysis(
    "Hierarchical Markov clustering",
    description="Hierarchically cluster the graph in place using Hierarchical Markov "
    + "clustering.",
    parameters=markov_params,
)


@hierarchical_markov_analysis
def hierarchical_markov(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    alpha: int = markov_params["alpha"].default,  # type: ignore
    beta: float = markov_params["beta"].default,  # type: ignore
    mu: float = markov_params["mu"].default,  # type: ignore
    max_iter: int = markov_params["max_iter"].default,  # type: ignore
    symmetrize: bool = markov_params["symmetrize"].default,  # type: ignore
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, Union[List[Node], List[str]]]:
    """docstring stub"""
    cluster_roots: List[Node] = [] if leafs is None else leafs  # type: ignore
    children: List[Node] = []

    while set(cluster_roots) != set(children) and len(cluster_roots) > 1:
        # Previous cluster_roots become children for new cluster level.
        children = cluster_roots
        graph, cluster_roots = markov(
            graph,
            root=None,
            leafs=children,
            inherit=inherit,
            loops=loops,
            edge_weights=edge_weights,
            alpha=alpha,
            beta=beta,
            mu=mu,
            inplace=True,  # Recursive calls may work in the given graph.
            max_iter=max_iter,
        )

    return graph, cluster_roots


markov_analysis = ClusterAnalysis(
    "Markov clustering",
    description="Cluster the graph in place using Markov Clustering.",
    parameters=markov_params,
)


@markov_analysis
def markov(
    graph: Graph,
    root: Optional[Union[str, Node]] = None,
    leafs: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = True,
    loops: bool = False,
    edge_weights: Optional[List[str]] = None,
    alpha: int = markov_params["alpha"].default,  # type: ignore
    beta: float = markov_params["beta"].default,  # type: ignore
    mu: float = markov_params["mu"].default,  # type: ignore
    max_iter: int = markov_params["max_iter"].default,  # type: ignore
    symmetrize: bool = markov_params["symmetrize"],  # type: ignore
    inplace: bool = True,
    names: bool = False,
    safe: bool = True,
    **kwargs,
) -> Tuple[Graph, Union[List[Node], List[str]]]:
    """docstring stub"""
    assert leafs is not None
    mat = graph.get_adjacency_matrix(leafs, inherit=inherit, loops=loops, only=edge_weights)
    assert isinstance(mat, np.ndarray)
    if symmetrize:
        mat = mat + mat.T  # Add transpose to get a guaranteed symmetrical matrix.
    tpm = calculate_tpm(mat, mu)
    if alpha > 1:  # Otherwise algorithm does nothing, then column max -> cluster ID.
        i = 0

        # TPM pruning threshold and equality tolerances.
        rtol = max(max_iter**-2, 1e-15)
        atol = max(max_iter**-3, 1e-15)
        bin_mat = mat > 0
        wmax = bin_mat.sum(axis=0).flatten().max()
        threshold = (mu * max(1.0, wmax)) ** -(alpha + 1)

        # TPM expansion/inflation loop
        tpm = prune_matrix(tpm, threshold)
        last_tpm = np.zeros_like(tpm)
        while not np.allclose(tpm, last_tpm, rtol=rtol, atol=atol) and i < max_iter:
            last_tpm = tpm.copy()

            tpm = np.linalg.matrix_power(tpm, alpha)  # Expansion step
            tpm = np.power(tpm, beta)  # Inflation step
            tpm = prune_matrix(tpm, threshold)  # Threshold step

            i += 1

    # Cluster IDs are row numbers of max values in columns.
    cluster_ids = tpm.argmax(0)
    cluster_roots = create_clusters(graph, leafs, cluster_ids)  # type: ignore

    return graph, cluster_roots


def calculate_tpm(matrix: np.ndarray, mu: float) -> np.ndarray:
    """Calculate Transfer Probability Matrix (TPM), which in turn is the sum of the
    Relative Influence and Relative Depencency Matrices (RIM, RDM).

    Arguments:
        matrix: Adjacency matrix.
        mu: Decay constant.

    Returns:
        Transfer Probability Matrix (TPM).
    """
    relative = MarkovRelative(matrix, mu)

    # Relative Influence Matrix (RIM). Percentage of influence originating from j on i.
    rim = relative.influence_matrix

    # Relative Dependency Matrix (RDM). Percentage of dependency of j on i.
    rdm = relative.dependency_matrix

    # Create Transfer Probability Matrix (TPM).
    tpm = rim + rdm

    # Set diagonal to maximum nonzero column entry. This enforces a suitable aperiodic
    # stochastic matrix.
    np.fill_diagonal(tpm, 0.0)
    colmax = tpm.max(axis=0)
    colmax[colmax == 0.0] = 1.0
    np.fill_diagonal(tpm, colmax)

    # Normalize each column for a column sum of 1.
    tpm = tpm / np.sum(tpm, 0)

    return tpm


def prune_matrix(matrix: np.ndarray, threshold: float) -> np.ndarray:
    """Return a column normalized matrix for which all values below the threshold have
    been pruned (set to 0.0).

    Arguments:
        matrix: Matrix to prune.
        threshold: Cut-off threshold for normalized values.

    Returns:
        Pruned matrix.
    """
    colsum = matrix.sum(0)
    to_prune = np.logical_and(matrix < threshold * colsum, matrix > 0)

    while to_prune.any():
        matrix[to_prune] = 0
        colsum = matrix.sum(0)
        to_prune = np.logical_and(matrix < threshold * colsum, matrix > 0)

    matrix = matrix / colsum
    return matrix


def create_clusters(graph: Graph, nodes: List[Node], cluster_ids: np.ndarray) -> List[Node]:
    """Assign nodes in graph to new cluster nodes using a numbered array.

    Arguments:
        graph: Graph to add clusters into.
        nodes: Nodes that were clustered.
        cluster_ids: 1D array with numbered cluster assignment per node.

    Returns:
        Current root nodes in the graph.
    """
    assert (
        len(nodes) == cluster_ids.size
    ), "Node count should match cluster IDs length. Found %d vs %d." % (
        len(nodes),
        cluster_ids.size,
    )

    # Transform cluster_ids to ranks of their unique values.
    # This makes them a perfect index sequence starting at 0.
    unique_ids, id_ranks = np.unique(cluster_ids, return_inverse=True)

    # Prepare children lists and fill them.
    children_lists: List[List[Node]] = [[] for i in unique_ids]
    for i, node in enumerate(nodes):
        rank = id_ranks[i]
        children_lists[rank].append(node)

    # Create cluster nodes and keep track of cluster roots.
    new_cluster_roots = []
    unchanged_cluster_roots = []
    for children in children_lists:
        if len(children) > 1:
            parent = create_parent(graph, children)
            new_cluster_roots.append(parent)
        # Node is it's own parent, don't change anything.
        else:
            unchanged_cluster_roots.append(children[0])

    return new_cluster_roots + unchanged_cluster_roots


class MarkovFlow:
    """Results of Markov steady-state flow analysis.

    Arguments:
        matrix: Adjacency matrix (non-negative, IR/FAD convention).
        mu: Evaporation constant (>1.0).

    Note:
        Solves the flow balance equation: A_s @ f + f_in = f, for which:
            * A_s: normalized adjacency matrix with added evaporation sink.
            * f_in: injection vector (1.0 for every node except sink).
            * f = inv(I - A_s) @ f_in (flow vector)
            * Q = inv(I - A_s) (sensitivity matrix)
            * f = Q @ f_in
            * F = A_s * f.T (edge flow matrix)
    """

    def __init__(self, matrix: np.ndarray, mu: float, scale: bool):
        self.matrix = matrix * (matrix > 0)
        self.mu = mu
        self.scale = scale

    @property
    def dim(self) -> int:
        """Adjacency matrix dimension."""
        return len(self.matrix)

    @property
    def sink_matrix(self) -> np.ndarray:
        """Column normalized adjacency matrix with an added evaporation sink."""
        return get_sink_matrix(self.matrix, self.mu)

    @property
    def sensitivity_matrix(self) -> np.ndarray:
        """Sensitivity matrix (Q) with respect to input flow. f = Q @ f_in."""
        try:
            mat = np.eye(self.dim + 1) - self.sink_matrix
            return np.linalg.inv(mat)
        except LinAlgError:
            markov_analysis.log(
                f"Error when trying to invert matrix of dim {self.dim}:\n"
                + f"{mat}\n\nCorresponding adjacency matrix:\n{self.matrix}."
            )
            raise

    @property
    def in_vector(self) -> np.ndarray:
        """Inflow vector used normally. 1.0 inflow at every node except the sink."""
        if self.scale:
            f_in = np.append(self.matrix.sum(axis=0), 0).reshape(self.dim + 1, 1)
        else:
            f_in = np.ones((self.dim + 1, 1))
            f_in[-1, 0] = 0
        return f_in

    @property
    def flow_vector(self) -> np.ndarray:
        """Flow through every node if system is injected with
        [`self.in_vector`][ragraph.analysis.cluster._markov.MarkovFlow.in_vector].
        """
        return self.sensitivity_matrix @ self.in_vector

    @property
    def flow_matrix(self) -> np.ndarray:
        """Flow over every edge if nodal flow equal
        [`self.flow_vector`][ragraph.analysis.cluster._markov.MarkovFlow.flow_vector].
        """
        return self.sink_matrix * self.flow_vector.T


class MarkovRelative:
    """Markov relative influence and dependency calculations.

    Arguments:
        adj: Adjacency matrix (non-negative, IR/FAD convention).
        mu: Evaporation constant (>1.0).

    Note:
        Solves specific cases of the Markov flow analysis where each node is injected
        with a flow of 1 to calculate the relative influence. The network is also
        reversed and injected again, which results in relative dependency.
    """

    def __init__(self, adj: np.ndarray, mu: float):
        self.adj = adj
        self.mu = mu

    @property
    def influence_matrix(self) -> np.ndarray:
        """Relative influence matrix (RIM).
        Percentage of influence originating from j on i.
        """
        return MarkovFlow(self.adj, self.mu, False).sensitivity_matrix[:-1, :-1]

    @property
    def dependency_matrix(self) -> np.ndarray:
        """Relative Dependency Matrix (RDM). Percentage of dependency of j on i."""
        return MarkovFlow(self.adj.T, self.mu, False).sensitivity_matrix[:-1, :-1].T


def get_sink_matrix(matrix: np.ndarray, mu: float) -> np.ndarray:
    """Calculate a normalized flow distribution matrix with an evaporation sink node.

    Arguments:
        matrix: Adjacency matrix.
        mu: Evaporation constant.

    Returns:
        Normalized flow distribution matrix with an added evaporation sink node at the
            bottom right.

    Note:
        Matrix structure of:
        ```
        [a00 a01 ... a0n 0]
        [a10 a11 ... a1n 0]
        [... ... ... ... .]
        [an0 an1 ... ann 0]
        [ e   e  ...  e  0]
        ```
        Where all columns are normalized [0.0, 1.0]
    """
    cont = 1 / mu
    evap = 1 - cont
    dim = len(matrix)
    S = matrix.sum(axis=0)  # Column sums.
    E = evap * np.ones((1, dim))  # Evaporation row.

    # Fixup edges with no outputs
    no_outputs = S == 0
    S[no_outputs] = 1.0
    E[:, no_outputs] = 1.0

    A_n = cont * matrix / S  # Normalized flow matrix [0,cont].

    # Add evaporation sink to adjacency matrix.
    # A_s = [[A_mu, 0], [evap, 0]]
    A_s = np.block([[A_n, np.zeros((dim, 1))], [E, np.zeros((1, 1))]])
    return A_s
