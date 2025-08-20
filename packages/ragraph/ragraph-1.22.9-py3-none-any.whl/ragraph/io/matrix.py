"""# Adjacency and mapping matrices support"""

from typing import Any, Dict, List, Optional, Union

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.generic import Convention

try:
    import numpy as np
except ImportError:
    np = None


def from_matrix(
    matrix: Union["np.ndarray", List[List[int]], List[List[float]]],
    rows: Optional[Union[List[Node], List[str]]] = None,
    cols: Optional[Union[List[Node], List[str]]] = None,
    weight_label: str = "default",
    empty: Optional[Union[int, float]] = 0.0,
    convention: Convention = Convention.IR_FAD,
    **graph_args: Dict[str, Any],
) -> Graph:
    """Create a graph from an adjacency or mapping matrix.

    Arguments:
        matrix: Matrix to convert into a graph.
        rows: Nodes or node labels corresponding to the rows of the matrix.
        cols: Nodes or node labels corresponding to the columns of the matrix. If none
            are provided, the row labels are re-used.
        weight_label: Weight label to use for matrix values.
        empty: Cell value to be considered "empty", e.g. no edge should be created.
        **graph_args: Additional arguments to [`Graph`][ragraph.graph.Graph] constructor.

    Returns:
        Graph object.

    Note:
        If no row labels are provided, they are generated in a "node#" format.
        If no column labels are provided, they are assumed to be equal to the rows.
        For non-square matrices, you should provide node labels!
    """

    rows = [Node(f"node{i}") for i in range(len(matrix))] if rows is None else rows

    # init empty graph
    graph = Graph(**graph_args)  # type: ignore

    # Parse row labels and create new nodes.
    node_rows = _parse_labels(graph, rows)

    # Init nodes from provided labels.
    if cols is None:
        node_cols = node_rows
    else:
        node_cols = _parse_labels(graph, cols)

    # Dimension check of matrix and labels.
    dim = (len(matrix), len(matrix[0]))
    labdim = (len(node_rows), len(node_cols))
    if dim != labdim:
        raise ValueError(f"Matrix dimensions {dim} do not agree with label dimensions {labdim}.")

    # Generate edges and return.
    if convention == Convention.IR_FAD:
        edges = [
            Edge(
                source,
                target,
                name=f"{source.name}->{target.name}",
                weights={weight_label: matrix[row][col]},
            )
            for row, target in enumerate(node_rows)
            for col, source in enumerate(node_cols)
            if matrix[row][col] != empty
        ]
    elif convention == Convention.IC_FBD:
        edges = [
            Edge(
                source,
                target,
                name=f"{source.name}->{target.name}",
                weights={weight_label: matrix[row][col]},
            )
            for row, source in enumerate(node_rows)
            for col, target in enumerate(node_cols)
            if matrix[row][col] != empty
        ]
    else:
        raise ValueError("Unknown convention for matrix conversion.")

    graph.edges = edges
    return graph


def to_matrix(
    graph: Graph,
    rows: Optional[Union[List[Node], List[str]]] = None,
    cols: Optional[Union[List[Node], List[str]]] = None,
    inherit: bool = False,
    loops: bool = False,
    only: Optional[List[str]] = None,
    convention: Convention = Convention.IR_FAD,
) -> Union["np.ndarray", List[List[float]]]:
    """Convert graph data into a directed numerical adjacency or mapping matrix.

    Arguments:
        graph: Graph to fetch data from.
        rows: Nodes representing the matrix rows.
        cols: Nodes representing the matrix columns if different from the rows.
        inherit: Whether to count weights between children of the given nodes.
        loops: Whether to calculate self-loops from a node to itself.
        only: Optional subset of edge weights to consider. See
            [`ragraph.edge.Edge`][ragraph.edge.Edge] for default edge weight implementation.

    Returns:
        Adjacency matrix as a 2D numpy array if numpy is present. Otherwise it will return a 2D
        nested list.

    Note:
        Note that the matrix is directed! Columns are inputs to rows.
    """
    if rows is None:
        rows = graph.leafs
    else:
        rows = [n if isinstance(n, Node) else graph.node_dict[n] for n in rows]

    if cols is None:
        cols = rows
    else:
        cols = [n if isinstance(n, Node) else graph.node_dict[n] for n in cols]

    dim = (len(rows), len(cols))
    if np:
        matrix = np.zeros(dim, dtype=float)
    else:
        matrix = [[0.0 for j in range(dim[1])] for i in range(dim[0])]

    for col, col_node in enumerate(cols):
        for row, row_node in enumerate(rows):
            if col_node == row_node and not loops:
                continue

            if convention == Convention.IR_FAD:
                source = col_node
                target = row_node
            elif convention == Convention.IC_FBD:
                source = row_node
                target = col_node
            else:
                raise ValueError("Unknown convention for matrix conversion.")

            sources = [source]
            targets = [target]

            if inherit:
                sources.extend(source.descendants)
                targets.extend(target.descendants)

            weight = sum(
                [_get_weight(e, only=only) for e in graph.edges_between_all(sources, targets)]
            )
            matrix[row][col] = float(weight)

    return matrix


def _parse_labels(graph: Graph, labels: Union[List[Node], List[str]]) -> List[Node]:
    """Parse matrix labels into a list of nodes."""
    nodes: List[Node] = [
        label if isinstance(label, Node) else graph.node_dict.get(str(label), Node(str(label)))
        for label in labels
    ]

    for node in nodes:
        graph.add_node(node)  # Skips existing identical nodes.

    return nodes


def _get_weight(e: Edge, only: Optional[List[str]] = None) -> float:
    """Get numerical weight from an edge."""
    if only:
        return sum(e.weights.get(k, 0.0) for k in only)
    else:
        return e.weight
