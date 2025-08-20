"""# Canopy by Ratio CASE format support"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union
from uuid import UUID

from ragraph.generic import Metadata
from ragraph.graph import Edge, Graph, Node

SCHEMA_PAT = re.compile(r"https://canopy.ratio-case.nl/schemas/v1/(\w+).schema.json")


def _match_schema(pat: str) -> Optional[str]:
    match = SCHEMA_PAT.match(pat)
    if match:
        return match.groups()[0]
    return None


def from_canopy(
    path: Union[str, Path],
) -> List[Graph]:
    """Get the graph(s) from a Canopy data file.

    Arguments:
        path: Path of the file to load.

    Returns:
        Graph objects contained in Canopy data formats being either a graph, tab,
        session, or workspace export of Canopy.

    Raises:
        InconsistencyError: if graph is inconsistent.
    """
    data = json.loads(Path(path).read_text())
    schema = _match_schema(data.get("$schema", ""))
    if schema == "workspace":
        graphs = list(_decode_workspace(data))
    elif schema == "session":
        graphs = list(_decode_session(data))
    elif schema == "tab":
        graphs = list(_decode_tab(data))
    else:
        graphs = [_decode_graph(data)]

    for graph in graphs:
        graph.check_consistency(raise_error=True)

    return graphs


def to_canopy(
    graph: Graph,
    path: Optional[Union[Path, str]] = None,
    fmt: str = "graph",
) -> Optional[str]:
    """Save graph as a Canopy dataset.

    Arguments:
        graph: Graph to save.
        path: Path to write to.
        fmt: One of 'session' or 'graph'.

    Returns:
        JSON encoded string if no path was provided to write to.
    """
    if fmt == "session":
        data = _encode_session(graph, schema=True)
    else:
        data = _encode_graph(graph, schema=True)
    if path is not None:
        enc = json.dumps(data)
        Path(path).write_text(enc, encoding="utf-8")
        return None
    else:
        enc = json.dumps(data, indent=2)
        return enc


def _encode_metadata(obj: Metadata, schema: bool = True) -> Dict[str, Any]:
    data: Dict[str, Any] = (
        {"$schema": "https://canopy.ratio-case.nl/schemas/v1/metadata.schema.json"}
        if schema
        else dict()
    )
    data.update(
        id=str(obj.uuid),
        name=obj.name,
        kind=obj.kind,
    )
    if obj.labels:
        data.update(labels=list(dict.fromkeys(obj.labels)))
    if obj.weights:
        data.update(weights={str(k): float(v) for k, v in obj.weights.items()})
    adict = obj.annotations.as_dict()
    if adict:
        data.update(annotations=adict)
    return data


def _encode_node(obj: Node, schema: bool = True) -> Dict[str, Any]:
    data: Dict[str, Any] = (
        {"$schema": "https://canopy.ratio-case.nl/schemas/v1/node.schema.json"}
        if schema
        else dict()
    )
    data.update(_encode_metadata(obj, schema=False))
    if obj.is_bus:
        data.update(isBus=bool(obj.is_bus))
    if obj.children:
        data.update(children=[str(n.uuid) for n in obj.children])
    return data


def _encode_edge(obj: Edge, schema: bool = True) -> Dict[str, Any]:
    data: Dict[str, Any] = (
        {"$schema": "https://canopy.ratio-case.nl/schemas/v1/edge.schema.json"}
        if schema
        else dict()
    )
    data.update(_encode_metadata(obj, schema=False))
    data.update(source=str(obj.source.uuid), target=str(obj.target.uuid))
    return data


def _encode_graph(obj: Graph, schema: bool = True) -> Dict[str, Any]:
    data: Dict[str, Any] = (
        {"$schema": "https://canopy.ratio-case.nl/schemas/v1/graph.schema.json"}
        if schema
        else dict()
    )
    data.update(_encode_metadata(obj, schema=False))
    if obj.nodes:
        data.update(
            dict(
                nodes=[_encode_node(n, schema=False) for n in obj.nodes],
            )
        )
    if obj.edges:
        data.update(
            dict(
                edges=[_encode_edge(e, schema=False) for e in obj.edges],
            )
        )
    return data


def _encode_session(graph: Graph, schema: bool = True) -> Dict[str, Any]:
    data: Dict[str, Any] = (
        {"$schema": "https://canopy.ratio-case.nl/schemas/v1/session.schema.json"}
        if schema
        else dict()
    )
    data.update(graph=_encode_graph(graph, schema=False))
    return data


def _decode_node(data: Dict[str, Any]) -> Node:
    opts = data.copy()
    opts.pop("$schema", None)
    opts["uuid"] = opts.pop("id", None)
    opts.pop("isBus", None)
    opts.pop("children", None)
    opts.pop("parent", None)
    return Node(**opts)


def _decode_hierarchy(data: Dict[str, Any], graph: Graph) -> None:
    for node_data in data.get("nodes", []):
        children = node_data.get("children")
        if not children:
            continue
        node = graph.node_uuid_dict[UUID(node_data.get("id"))]
        node.children = [graph.node_uuid_dict[UUID(uuid)] for uuid in children]
    for node_data in data.get("nodes", []):
        if node_data.get("isBus"):
            node = graph.node_uuid_dict[UUID(node_data["id"])]
            if node.parent:
                node.is_bus = True


def _decode_edge(data: Dict[str, Any], graph: Graph) -> Edge:
    opts = data.copy()
    opts.pop("$schema", None)
    opts["uuid"] = opts.pop("id", None)
    opts["source"] = graph.node_uuid_dict[UUID(data["source"])]
    opts["target"] = graph.node_uuid_dict[UUID(data["target"])]
    return Edge(**opts)


def _decode_graph(data: Dict[str, Any]) -> Graph:
    opts = data.copy()
    opts.pop("$schema", None)
    opts["uuid"] = opts.pop("id", None)
    opts.pop("nodes", None)
    opts.pop("edges", None)
    graph = Graph(**opts)
    graph.nodes = [_decode_node(node_data) for node_data in data.get("nodes", [])]
    _decode_hierarchy(data, graph)
    graph.edges = [_decode_edge(edge_data, graph) for edge_data in data.get("edges", [])]
    return graph


def _decode_tab(data: Dict[str, Any]) -> Generator[Graph, None, None]:
    if isinstance(data.get("graph"), dict):
        yield _decode_graph(data["graph"])


def _decode_session(data: Dict[str, Any]) -> Generator[Graph, None, None]:
    if isinstance(data.get("graph"), dict):
        yield _decode_graph(data["graph"])
    for tab_data in data.get("tabs", []):
        if isinstance(tab_data, dict):
            yield from _decode_tab(tab_data)


def _decode_workspace(data: Dict[str, Any]) -> Generator[Graph, None, None]:
    for graph_data in data.get("graphs", []):
        yield _decode_graph(graph_data)
    for session_data in data.get("sessions", []):
        yield from _decode_session(session_data)
    for tab_data in data.get("tabs", []):
        yield from _decode_tab(tab_data)
