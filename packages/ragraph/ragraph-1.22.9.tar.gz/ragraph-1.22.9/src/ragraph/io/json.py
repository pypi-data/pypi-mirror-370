"""# JSON format support"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import UUID

from ragraph.edge import Edge
from ragraph.generic import Annotations
from ragraph.graph import Graph
from ragraph.node import Node


class GraphEncoder(json.JSONEncoder):
    def default(self, obj):
        if (
            isinstance(obj, Graph)
            or isinstance(obj, Edge)
            or isinstance(obj, Node)
            or isinstance(obj, Annotations)
        ):
            return obj.json_dict
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.encode(obj)


def graph_from_json_dict(graph_dict: Dict[str, Any], use_uuid: bool = True) -> Graph:
    """Recreate Graph object from JSON dictionary."""
    nodes = graph_dict.get("nodes", dict())
    edges = graph_dict.get("edges", dict())
    g = Graph(
        name=graph_dict.get("name"),
        kind=graph_dict.get("kind"),
        labels=graph_dict.get("labels"),
        weights=graph_dict.get("weights"),
        annotations=graph_dict.get("annotations"),
        uuid=graph_dict.get("uuid"),
    )

    # Get node dictionaries.
    if isinstance(nodes, dict):
        node_dicts = list(nodes.values())
    elif isinstance(nodes, list):
        node_dicts = nodes
    else:
        raise ValueError("Unrecognizable nodes property.")

    # Get edge dictionaries.
    if isinstance(edges, dict):
        edge_dicts = list(edges.values())
    elif isinstance(edges, list):
        edge_dicts = edges
    else:
        raise ValueError("Unrecognizable edges property.")

    # Add initial nodes.
    for nd in node_dicts:
        g.add_node(
            Node(
                name=nd.get("name"),
                kind=nd.get("kind"),
                labels=nd.get("labels"),
                parent=None,
                children=[],
                weights=nd.get("weights"),
                annotations=nd.get("annotations"),
                uuid=nd.get("uuid"),
            )
        )

    node_ref = {str(node.uuid): node for node in g.nodes} if use_uuid else g.node_dict
    ref_key = "uuid" if use_uuid else "name"

    # Resolve references.
    for nd in node_dicts:
        if nd.get("parent", False):
            node_ref[nd[ref_key]].parent = node_ref[nd["parent"]]
        if nd.get("children", False):
            node_ref[nd[ref_key]].children = [node_ref[c] for c in nd["children"]]
        if nd.get("is_bus", False):
            node_ref[nd[ref_key]].is_bus = True

    # Add edges.
    for ed in edge_dicts:
        g.add_edge(
            Edge(
                node_ref[ed["source"]],
                node_ref[ed["target"]],
                name=ed.get("name"),
                kind=ed.get("kind"),
                labels=ed.get("labels"),
                weights=ed.get("weights"),
                annotations=ed.get("annotations"),
                uuid=ed.get("uuid"),
            ),
        )

    return g


def from_json(
    path: Optional[Union[str, Path]] = None,
    enc: Optional[str] = None,
    use_uuid: bool = True,
) -> Graph:
    """Decode JSON file or string into a Graph.

    Arguments:
        path: JSON file path.
        enc: JSON encoded string.

    Returns:
        Graph object.
    """
    if path is None and enc is None:
        raise ValueError("`path` and `enc` arguments cannot both be `None`.")
    if path is not None and enc is not None:
        raise ValueError("`path` and `enc` arguments cannot both be set.")

    if path:
        enc = Path(path).read_text(encoding="utf-8")

    json_dict = json.loads(enc)

    return graph_from_json_dict(json_dict, use_uuid=use_uuid)


def to_json(graph: Graph, path: Optional[Union[str, Path]] = None) -> Optional[str]:
    """Encode Graph to JSON file or string.

    Arguments:
        path: Optional file path to write JSON to.

    Returns:
        JSON string.
    """

    enc = json.dumps(graph, cls=GraphEncoder, sort_keys=True, indent=4)
    if path is not None:
        path = Path(path)
        path.write_text(enc, encoding="utf-8")
        return None
    else:
        return enc
