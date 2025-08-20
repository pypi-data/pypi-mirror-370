"""# Similarity analysis"""

from typing import Any, Callable, List, Tuple

import numpy as np

from ragraph.analysis import cluster, similarity
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node


class SimilarityAnalysis:
    """Similarity analysis of nodes based upon mutual mapping relations.

    Arguments:
        cols: List of column nodes.
        rows: List of row nodes.
        edges: List of edges from column nodes to row nodes to be used in similarity
            analysis.
        col_sim_threshold: Column similarity threshold. Values below this threshold are
            pruned from the similarity matrix and the corresponding edges are removed.
            Defaults to 0.0 (no threshold).
        row_sim_threshold: Column similarity threshold. Values below this threshold are
            pruned from the similarity matrix and the corresponding edges are removed.
            Defaults to 0.0 (no threshold).

    Class Attributes:
        similarity_kind: Edge kind for similarity edges. Defaults to ``similarity``.

    Note:
        A mapping matrix relating M column nodes to N row nodes is used as input for
        the similarity analysis.
    """

    similarity_kind = "similarity"

    def __init__(
        self,
        rows: List[Node],
        cols: List[Node],
        edges: List[Edge],
        col_sim_threshold: float = 0.0,
        row_sim_threshold: float = 0.0,
    ):
        self._cols: List[Node] = []
        self._rows: List[Node] = []
        self._edges: List[Edge] = []
        self._col_sim_threshold = 0.0
        self._row_sim_threshold = 0.0
        self._graph: Graph = None  # type: ignore

        self.cols = cols
        self.rows = rows
        self.edges = edges
        self.col_sim_threshold = col_sim_threshold
        self.row_sim_threshold = row_sim_threshold

    @property
    def rows(self) -> List[Node]:
        """List of rows nodes."""
        return self._rows

    @rows.setter
    def rows(self, value: List[Node]):
        kinds = set([n.kind for n in value])
        if len(kinds) > 1:
            raise ValueError(
                f"""All row nodes must be of the same kind. Found node kinds:
                 {kinds}."""
            )

        if self._rows:
            self._rows = value
            self.update_graph()
        else:
            self._rows = value

    @property
    def cols(self) -> List[Node]:
        """List of column nodes."""
        return self._cols

    @cols.setter
    def cols(self, value: List[Node]):
        kinds = set([n.kind for n in value])
        if len(kinds) > 1:
            raise ValueError(
                f"""All columns nodes must be of the same kind. Found node kinds:
                 {kinds}."""
            )

        if self._cols:
            self._cols = value
            self.update_graph()
        else:
            self._cols = value

    @property
    def edges(self) -> List[Edge]:
        """List of edges."""
        return self._edges

    @edges.setter
    def edges(self, value: List[Edge]):
        if self._edges:
            self._edges = value
            self.update_graph()
        else:
            self._edges = value

    @property
    def row_sim_threshold(self) -> float:
        """Similarity threshold. Values below this threshold are pruned from the
        row similarity matrix and the corresponding edges are removed.
        """
        return self._row_sim_threshold

    @row_sim_threshold.setter
    def row_sim_threshold(self, value: float):
        if value < 0.0 or value >= 1.0:
            raise ValueError(
                f"""Similarity threshold must have a value between 0.0 and 1.0. Found
                value: {value}."""
            )

        if self._row_sim_threshold is not None:
            self._row_sim_threshold = float(value)
            self.update_row_similarity()
        else:
            self._row_sim_threshold = float(value)

    @property
    def col_sim_threshold(self) -> float:
        """Similarity threshold. Values below this threshold are pruned from the
        column similarity matrix and the corresponding edges are removed.
        """
        return self._col_sim_threshold

    @col_sim_threshold.setter
    def col_sim_threshold(self, value: float):
        if value < 0.0 or value >= 1.0:
            raise ValueError(
                f"""Similarity threshold must have a value between 0.0 and 1.0. Found
                value: {value}."""
            )

        if self._col_sim_threshold is not None:
            self._col_sim_threshold = float(value)
            self.update_col_similarity()
        else:
            self._col_sim_threshold = float(value)

    @property
    def graph(self) -> Graph:
        """Graph containing similarity edges."""
        if self._graph:
            return self._graph
        else:
            self.update_graph()
            return self._graph

    @property
    def row_similarity_matrix(self) -> np.ndarray:
        """The row similarity matrix based on their mapping row."""
        jaccard = similarity.jaccard_matrix(self.rows, self.row_mapping)
        jaccard[jaccard < self.row_sim_threshold] = 0.0
        return jaccard

    @property
    def col_similarity_matrix(self) -> np.ndarray:
        """The column similarity matrix based on their mapping column."""
        jaccard = similarity.jaccard_matrix(self.cols, self.col_mapping)
        jaccard[jaccard < self.col_sim_threshold] = 0.0
        return jaccard

    def update_graph(self) -> None:
        """Update Internal similarity graph"""
        self._graph = Graph(nodes=self.cols + self.rows, edges=self.edges)
        self.update_col_similarity()
        self.update_row_similarity()

    def update_row_similarity(self) -> None:
        """Update Jaccard Row Similarity Index edges between (clustered) rows."""
        self._update_similarity(self.rows, self.row_similarity_matrix)

    def update_col_similarity(self) -> None:
        """Update Jaccard Column Similarity Index edges between (clustered) columns."""
        self._update_similarity(self.cols, self.col_similarity_matrix)

    def _update_similarity(self, nodes: List[Node], mat: np.ndarray) -> None:
        """Update Jaccard Similarity Index edges between (clustered) nodes."""
        if not self.graph:
            self.update_graph()

        for e in [
            edge
            for edge in self.graph.edges_between_all(nodes, nodes)
            if edge.kind == self.similarity_kind
        ]:
            self.graph.del_edge(e)

        for row, target in enumerate(nodes):
            for col, source in enumerate(nodes):
                if row == col:
                    continue
                sim = mat[row][col]
                if not sim:
                    continue
                self.graph.add_edge(
                    Edge(
                        source,
                        target,
                        kind=self.similarity_kind,
                        weights=dict(similarity=mat[row][col]),
                    )
                )

    def cluster_rows(
        self,
        algo: Callable[[Graph, Any], Tuple[List[Node]]] = cluster.markov,
        **algo_args: Any,
    ) -> None:
        """Cluster column nodes based on their similarity. Updates Graph in-place.

        Arguments:
            algo: Clustering algorithm. Should take a graph as first argument and cluster it
                in-place. Defaults to [`cluster.markov`][ragraph.analysis.cluster.markov].
            **algo_args: Algorithm arguments. See
                [`cluster.markov`][ragraph.analysis.cluster.markov] for sensible defaults.
        """
        self._cluster(self.rows, algo, **algo_args)

    def cluster_cols(
        self,
        algo: Callable[[Graph, Any], Tuple[List[Node]]] = cluster.markov,
        **algo_args: Any,
    ) -> None:
        """Cluster column nodes based on their similarity. Updates Graph in-place.

        Arguments:
            algo: Clustering algorithm. Should take a graph as first argument and cluster it
                in-place. Defaults to [`cluster.markov`][ragraph.analysis.cluster.markov].
            **algo_args: Algorithm arguments. See
                [`cluster.markov`][ragraph.analysis.cluster.markov] for sensible defaults.
        """
        self._cluster(self.cols, algo, **algo_args)

    def _cluster(
        self,
        leafs: List[Node],
        algo: Callable[[Graph, Any], Tuple[List[Node]]] = cluster.markov,
        **algo_args: Any,
    ) -> None:
        """Cluster column nodes based on their similarity. Updates Graph in-place.

        Arguments:
            leafs: List of row or column nodes to be clustered.
            algo: Clustering algorithm. Should take a graph as first argument and cluster it
                in-place. Defaults to [`cluster.markov`][ragraph.analysis.cluster.markov].
            **algo_args: Algorithm arguments. See
                [`cluster.markov`][ragraph.analysis.cluster.markov] for sensible defaults.
        """
        algo(self.graph, leafs=leafs, **algo_args, inplace=True)  # type: ignore

    def row_mapping(self, row: Node) -> List[bool]:
        """Boolean possession checklist for a row node w.r.t.
        [`self.cols`][ragraph.analysis.similarity.SimilarityAnalysis.cols]."""
        return [self.check_mapping(col, row) for col in self.cols]

    def col_mapping(self, col: Node) -> List[bool]:
        """Boolean possession checklist for a column node w.r.t.
        [`self.rows`][ragraph.analysis.similarity.SimilarityAnalysis.rows]."""
        return [self.check_mapping(col, row) for row in self.rows]

    def check_mapping(self, col: Node, row: Node) -> bool:
        """Check whether a column node maps to a row node."""
        if len(self.graph.directed_edges[col.name][row.name]) > 0:
            return True
        else:
            return False
