"""# CSV format support"""

import csv
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ragraph.generic import Annotations
from ragraph.graph import Edge, Graph, Node

NODE_COLUMNS = ["name", "uuid", "kind", "labels", "parent", "children", "is_bus"]
EDGE_COLUMNS = ["source", "target", "name", "uuid", "kind", "labels"]


def from_csv(
    nodes_path: Optional[Union[str, Path]] = None,
    edges_path: Optional[Union[str, Path]] = None,
    csv_delimiter: str = ";",
    iter_delimiter: str = ";",
    node_weights: Optional[List[str]] = None,
    edge_weights: Optional[List[str]] = None,
    **graph_kwargs: Any,
) -> Graph:
    """Convert CSV files to a graph.

    Nodes file (optional) requires at least a `name` column. Optional special
    property columns are `kind`, `labels`, `parent`, `children` and `is_bus`.

    Edges file requires at least a `source` and `target` column. Optional special
    property columns are `kind` and `labels`.

    Automatically completes one sided parent-child relationships.

    Arguments:
        nodes_path: Path of optional nodes CSV file.
        edges_path: Path of edges CSV file.
        csv_delimiter: Delimiter of CSV file.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        node_weights: Columns to interpret as node weights.
        edge_weights: Columns to interpret as edge weights.
        **graph_kwargs: Optional [`Graph`][ragraph.graph.Graph] arguments when instantiating.

    Returns:
        Graph object.

    Raises:
        InconsistencyError: if graph is inconsistent.
    """
    graph = Graph(**graph_kwargs)

    if not nodes_path and not edges_path:
        return graph

    if not node_weights:
        node_weights = []

    if not edge_weights:
        edge_weights = []

    if nodes_path:
        node_dict = _load_nodes(nodes_path, csv_delimiter, iter_delimiter, node_weights)
    else:
        node_dict = _derive_nodes(edges_path, csv_delimiter)

    if edges_path:
        edges = _load_edges(edges_path, csv_delimiter, iter_delimiter, node_dict, edge_weights)
    else:
        edges = []

    graph.add_parents = True
    graph.add_children = True
    graph.nodes = node_dict
    graph.edges = edges
    graph.check_consistency(raise_error=True)
    return graph


def to_csv(
    graph: Graph,
    stem_path: Union[str, Path],
    csv_delimiter: str = ";",
    iter_delimiter: str = ";",
    use_uuid: bool = False,
):
    """Save graph to nodes and edges CSV files.

    Arguments:
        graph: Graph to save.
        stem_path: Stem path for output CSV's. Appended with _nodes.csv and _edges.csv.
        csv_delimiter: CSV delimiter.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        use_uuid: Whether to export UUIDs, too.
    """
    stem_path = Path(stem_path)

    nodes_fname = stem_path.name + "_nodes.csv"
    nodes_path = stem_path.with_name(nodes_fname)
    _save_nodes(graph, nodes_path, csv_delimiter, iter_delimiter, use_uuid=use_uuid)

    edges_fname = stem_path.name + "_edges.csv"
    edges_path = stem_path.with_name(edges_fname)
    _save_edges(graph, edges_path, csv_delimiter, iter_delimiter, use_uuid=use_uuid)


def _load_nodes(
    fpath: Union[str, Path],
    csv_delimiter: str,
    iter_delimiter: str,
    node_weights: List[str],
) -> Dict[str, Node]:
    """Convert node CSV file to a list of nodes.

    Arguments:
        fpath: Path to nodes CSV file.
        csv_delimiter: CSV delimiter.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        node_weights: Columns to interpret as node weights.

    Returns:
        Node dictionary (name, node).
    """
    with Path(fpath).open(newline="") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        columns = reader.fieldnames
        rows = [row for row in reader]
    if "name" not in columns:
        raise ValueError(
            "Nodes CSV file {} needs at least a 'name' column, found {}.".format(
                str(fpath), columns
            )
        )

    wght_cols = node_weights
    anno_cols = [col for col in columns if col not in NODE_COLUMNS and col not in wght_cols]

    # Handle node names and annotations
    names = []
    nodes = []
    for row in rows:
        name = row["name"]
        anno = Annotations(**{col: row[col] for col in anno_cols})
        weights = {
            col: _convert_to_num(row[col])
            for col in wght_cols
            if row[col] != "" and row[col] is not None
        }
        names.append(name)
        uuid = row.get("uuid", None)
        nodes.append(Node(name, weights=weights, annotations=anno, uuid=uuid))

    if len(names) != len(set(names)):
        raise ValueError("Node names are not unique.")

    # Update other values including references
    node_dict = OrderedDict(zip(names, nodes))
    for row in rows:
        name = row["name"]
        node = node_dict[name]

        kind = row.get("kind", None)
        if kind:
            node.kind = str(kind)

        labels = row.get("labels", None)
        if labels:
            node.labels = [s.strip() for s in labels.split(iter_delimiter)]

        parent = row.get("parent", None)
        if parent:
            node.parent = node_dict[parent]

        children = row.get("children", [])
        if children:
            children_names = [n.strip() for n in children.split(iter_delimiter)]
            children = [node_dict[n] for n in children_names if node_dict[n] not in node.children]
            node.children = node.children + children

        is_bus = row.get("is_bus", "false")
        if is_bus.strip().lower() == "true":
            node.is_bus = True

    return node_dict


def _derive_nodes(edges_path: Optional[Union[str, Path]], csv_delimiter: str) -> Dict[str, Node]:
    """Derive nodes from edges CSV file.

    Arguments:
        edges_path: Path to edges CSV file.
        csv_delimiter: CSV delimiter.

    Returns:
        Node dictionary (name, node).
    """
    if not edges_path:
        return OrderedDict()

    with Path(edges_path).open(newline="") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        columns = reader.fieldnames or []
        rows = [row for row in reader]
    if "source" not in columns or "target" not in columns:
        raise ValueError(
            "Edges CSV file {} needs at least a 'source' and 'target' column.".format(
                str(edges_path)
            )
        )

    nodes = []
    names = []
    for row in rows:
        source = row["source"]
        if source not in names:
            nodes.append(Node(source))
            names.append(source)
        target = row["target"]
        if target not in names:
            nodes.append(Node(target))
            names.append(target)

    return OrderedDict(zip(names, nodes))


def _load_edges(
    fpath: Union[str, Path],
    csv_delimiter: str,
    iter_delimiter: str,
    node_dict: List[Node],
    edge_weights: List[str],
) -> List[Edge]:
    """Convert edge CSV file to graph.

    Arguments:
        fpath: Path to edges CSV file.
        csv_delimiter: CSV delimiter.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        node_dict: Node dictionary (name, node).
        edge_weights: Columns to interpret as edge weights.

    Returns:
        Edge list.
    """

    with Path(fpath).open(newline="") as f:
        reader = csv.DictReader(f, delimiter=csv_delimiter)
        columns = reader.fieldnames
        rows = [row for row in reader]
    if "source" not in columns or "target" not in columns:
        raise ValueError(
            "Edges CSV file {} needs at least a 'source' and 'target' column.".format(str(fpath))
        )

    wght_cols = edge_weights
    anno_cols = [col for col in columns if col not in EDGE_COLUMNS and col not in wght_cols]

    edges = []
    for row in rows:
        if row.get("labels", None):
            row["labels"] = [s.strip() for s in row["labels"].split(iter_delimiter)]
        weights = {
            col: _convert_to_num(row[col])
            for col in wght_cols
            if row[col] != "" and row[col] is not None
        }
        anno = Annotations(**{col: row[col] for col in anno_cols})
        kwargs = {col: row[col] for col in columns if col in EDGE_COLUMNS}
        kwargs["source"] = node_dict[kwargs["source"]]
        kwargs["target"] = node_dict[kwargs["target"]]
        edges.append(Edge(**kwargs, weights=weights, annotations=anno))

    return edges


def _save_nodes(
    graph: Graph,
    fpath: Path,
    csv_delimiter: str,
    iter_delimiter: str,
    use_uuid: bool = False,
):
    """Save graph nodes to CSV file.

    Arguments:
        graph: Graph to save.
        fpath: Path to nodes CSV file.
        csv_delimiter: CSV delimiter.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        use_uuid: Whether to export UUIDs, too.
    """
    # Weights column mapping
    wght_keys = [key for key in graph.node_weight_labels if key is not None]
    wght_map = {key: str(key) for key in wght_keys}
    wght_map.update({key: str(key) + "_weight" for key in wght_keys if str(key) in NODE_COLUMNS})

    # Annotations column mapping
    anno_keys = sorted(set([key for node in graph.node_list for key in node.annotations.keys()]))
    anno_map = {key: str(key) for key in anno_keys}
    anno_map.update(
        {
            key: str(key) + "_annotation"
            for key in anno_keys
            if str(key) in NODE_COLUMNS or str(key) in wght_map.values()
        }
    )

    row_dict = dict()
    for key in NODE_COLUMNS:
        row_dict[key] = None
    for key in wght_map.values():
        row_dict[key] = None
    for key in anno_map.values():
        row_dict[key] = None
    if not use_uuid:
        row_dict.pop("uuid")

    fpath = Path(fpath)
    with fpath.open(mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row_dict.keys(), delimiter=csv_delimiter)
        writer.writeheader()

        for node in graph.node_list:
            row_dict["name"] = node.name
            if use_uuid:
                row_dict["uuid"] = str(node.uuid)
            row_dict["kind"] = node.kind
            row_dict["labels"] = iter_delimiter.join(node.labels)
            if node.parent:
                row_dict["parent"] = node.parent.name
            else:
                row_dict["parent"] = None
            child_str = iter_delimiter.join([c.name for c in node.children])
            if child_str:
                row_dict["children"] = child_str
            else:
                row_dict["children"] = None
            row_dict["is_bus"] = node.is_bus

            for key, value in wght_map.items():
                row_dict[value] = node.weights[key]

            for key, value in anno_map.items():
                row_dict[value] = getattr(node.annotations, key, None)

            writer.writerow(row_dict)


def _save_edges(
    graph: Graph,
    fpath: Path,
    csv_delimiter: str,
    iter_delimiter: str,
    use_uuid: bool = False,
):
    """Save graph edges to CSV file.

    Arguments:
        graph: Graph to save.
        fpath: Path to edges CSV file.
        csv_delimiter: CSV delimiter.
        iter_delimiter: Iterable delimiter (i.e. for children names list).
        use_uuid: Whether to export UUIDs, too.
    """
    # Weights column mapping
    wght_keys = [key for key in graph.edge_weight_labels if key is not None]
    wght_map = {key: str(key) for key in wght_keys}
    wght_map.update({key: str(key) + "_weight" for key in wght_keys if str(key) in EDGE_COLUMNS})

    # Annotations column mapping
    anno_keys = sorted(set([key for edge in graph.edge_list for key in edge.annotations.keys()]))
    anno_map = {key: str(key) for key in anno_keys}
    anno_map.update(
        {
            key: str(key) + "_annotation"
            for key in anno_keys
            if str(key) in NODE_COLUMNS or str(key) in wght_map.values()
        }
    )

    row_dict = dict()
    for key in EDGE_COLUMNS:
        row_dict[key] = None
    for key in wght_map.values():
        row_dict[key] = None
    for key in anno_map.values():
        row_dict[key] = None
    if not use_uuid:
        row_dict.pop("uuid")

    fpath = Path(fpath)
    with fpath.open(mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row_dict.keys(), delimiter=csv_delimiter)
        writer.writeheader()

        for edge in graph.edge_list:
            row_dict["name"] = edge.name
            row_dict["source"] = edge.source.name
            row_dict["target"] = edge.target.name
            row_dict["kind"] = edge.kind
            row_dict["labels"] = iter_delimiter.join(edge.labels)
            if use_uuid:
                row_dict["uuid"] = str(edge.uuid)

            for key, value in wght_map.items():
                row_dict[value] = edge.weights.get(key, None)

            for key, value in anno_map.items():
                row_dict[value] = getattr(edge.annotations, key, None)

            writer.writerow(row_dict)


def _convert_to_num(value: str) -> Union[float, bool]:
    """Convert a string value to a float number or bool.

    Argument:
        value: The value to be converted.
    """
    if not isinstance(value, str):
        return value

    if value.strip().lower() == "true":
        return True
    elif value.strip().lower() == "false":
        return False
    else:
        try:
            # String is a number
            num = float(value)
            return num
        except ValueError:
            msg = " ".join(
                [
                    "You are assigning a string as a weight property.",
                    "Please use a float, integer, or a Bool.",
                    "A default value of 1.0 is used as a replacement for {}.".format(value),
                ]
            )
            warnings.warn(msg)
            return 1.0
